#!/usr/bin/env python3
# language101 scraper helps you scrape full language courses from sites like
# japanesepod101.com, spanishpod101.com, chineseclass101.com and more!

import argparse
import time
import json
import os
import re
import requests
import sys


from random import randint
from sys import exit
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from http.cookiejar import MozillaCookieJar
from urllib.parse import urlparse


CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

def load_config():
    """Load configuration from config.json"""
    try:
        if not os.path.exists(CONFIG_FILE):
            return None
            
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

def save_config(username, password):
    """Save configuration to config.json"""
    try:
        config = {
            'username': username,
            'password': password
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print("Credentials saved to config.json")
    except Exception as e:
        print(f"Error saving config: {e}")

parser = argparse.ArgumentParser(description='Scrape full language courses by Innovative Language.')
parser.add_argument('-u', '--username', help='Username (email)')
parser.add_argument('-p', '--password', help='Password for the course')
parser.add_argument('--url', help='URL for the first lesson of the course')

args = parser.parse_args()

config = load_config()

# If credentials are provided via command line, use those
if args.username and args.password:
    USERNAME = args.username
    PASSWORD = args.password
    # Save the new credentials
    save_config(USERNAME, PASSWORD)
elif config:
    USERNAME = config['username']
    PASSWORD = config['password']
else:
    USERNAME = input('Username (email): ')
    PASSWORD = input('Password: ')
    # Save the entered credentials
    save_config(USERNAME, PASSWORD)
COURSE_URL = args.url or input('Please insert first lesson URL of the desired course, for example:\n'
                               '* https://www.japanesepod101.com/lesson/lower-beginner-1-a-formal-japanese'
                               '-introduction/?lp=116\n '
                               '* https://www.spanishpod101.com/lesson/basic-bootcamp-1-a-pleasure-to-meet-you/?lp'
                               '=425\n '
                               '* https://www.chineseclass101.com/lesson/absolute-beginner-1-meeting-whats-your-name'
                               '/?lp=208\n')

LOGIN_DATA = {
    'amember_login': USERNAME,
    'amember_pass': PASSWORD,
}

obj = urlparse(COURSE_URL)
SOURCE_URL = f'{obj.scheme}://{obj.netloc}'
LOGIN_URL = f'{SOURCE_URL}/member/login_new.php'

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE = os.path.join(SCRIPT_DIR, 'cookies.txt')
UA_FILE = os.path.join(SCRIPT_DIR, 'ua.txt')


def save_cookies(session, filename=COOKIES_FILE):
    """Save session cookies to a Netscape format cookie file"""
    cookie_jar = MozillaCookieJar(filename)
    # Copy cookies from session to cookie jar
    for cookie in session.cookies:
        cookie_jar.set_cookie(cookie)
    cookie_jar.save(ignore_discard=True, ignore_expires=True)
    print(f"Cookies saved to {filename}")

def load_cookies(filename=COOKIES_FILE):
    """Load Netscape format cookies from file into a new session"""
    session = requests.Session()
    try:
        cookie_jar = MozillaCookieJar(filename)
        cookie_jar.load(ignore_discard=True, ignore_expires=True)
        session.cookies = requests.cookies.RequestsCookieJar()
        for cookie in cookie_jar:
            session.cookies.set_cookie(cookie)
        print(f"Cookies loaded from {filename}")
        return session
    except FileNotFoundError:
        print(f"No cookie file found at {filename}")
        return None

def load_ua(filename=UA_FILE):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print('Error: Please make a "ua.txt" file containing the User Agent of your browser in the directory of the python script.'
            + 'You can display your User Agent at https://dnschecker.org/user-agent-info.php.')
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    exit(1)

# Function to extract numeric prefixes with leading zeros
def get_existing_prefixes(directory):
    prefixes = set()
    for filename in os.listdir(directory):
        match = re.match(r"^(\d+)", filename)
        if match:
            prefixes.add(match.group(1))  # Add the number as a string (preserving leading zeros)
    return prefixes

def check_for_captcha(soup_or_element):
    """
    Check if a BeautifulSoup element contains captcha text
    Returns True if captcha is detected, False otherwise
    """
    try:
        element_text = soup_or_element.get_text().lower()
        return "captcha" in element_text
    except Exception as e:
        print(f"Error checking for captcha: {e}")
        return False


def check_login_required(html_content):
    """Check if the page contains a sign in button"""
    soup = BeautifulSoup(html_content, 'lxml')
    sign_in_buttons = soup.find_all(['button', 'a'], string=re.compile(r'Sign In', re.IGNORECASE))
    return len(sign_in_buttons) > 0

def check_http_error(response, fail_safe=False):
    if response.status_code == 200:
        return True
    elif response.status_code >= 400:
        if response.status_code == 403:
            print("Error: 403 Forbidden")
        elif response.status_code == 404:
            print("Error: 404 Resource not found.")
        elif response.status_code == 500:
            print("Error: 500 Server error.")
        else:
            print(f"Error: Received status code {response.status_code}")
    else:
        print(f"Received unexpected status code: {response.status_code}")
    if fail_safe:
        return False
    exit(1)

class MediaDownloader:
    def __init__(self, session, source_url, save_dir='.'):
        self.session = session
        self.source_url = source_url
        self.invalid_chars = r'\/:*?"<>|'  # Fixed invalid escape sequence
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def clean_filename(self, text):
        """Remove invalid characters from filename"""
        for char in self.invalid_chars:
            text = text.replace(char, "")
        return text

    def create_filename(self, title, suffix, extension):
        """Create a standardized filename"""
        clean_title = self.clean_filename(title)
        return f'{clean_title} - {suffix}{extension}'

    def get_lesson_dir(self, file_prefix, title):
        """Create a directory for each lesson"""
        clean_title = self.clean_filename(title)
        # Use just the lesson number as the directory name for cleaner structure
        lesson_dir = os.path.join(self.save_dir, file_prefix)
        os.makedirs(lesson_dir, exist_ok=True)
        return lesson_dir

    def download_file(self, file_url, file_name, title, file_prefix):
        """Download and save a file in the lesson's directory"""
        # Create lesson-specific directory
        lesson_dir = self.get_lesson_dir(file_prefix, title)
        full_path = os.path.join(lesson_dir, file_name)
        
        # Skip if file already exists
        if os.path.exists(full_path):
            print(f'\tSkipping {file_name} (already exists)')
            return False

        try:
            response = self.session.get(file_url)
            ok = check_http_error(response, True)
            if not ok:
                return
            
            # Create lesson-specific directory
            lesson_dir = self.get_lesson_dir(file_prefix, title)
            full_path = os.path.join(lesson_dir, file_name)
            
            with open(full_path, 'wb') as f:
                f.write(response.content)
            print(f'\t{file_name} saved in {os.path.basename(lesson_dir)}')
            return True
        except Exception as e:
            print(f'\tFailed to save {file_name}: {e}')
            return False

    def get_file_url(self, element, url_attributes):
        """Extract file URL from element using multiple possible attributes"""
        for attr in url_attributes:
            try:
                url = element[attr]
                if not url.startswith('http'):
                    url = self.source_url + url
                return url
            except (KeyError, AttributeError):
                continue
        return None

class MediaProcessor:
    def __init__(self, session, source_url, save_dir='.'):
        self.downloader = MediaDownloader(session, source_url, save_dir)
        
    def process_audio(self, soup, file_prefix):
        """Process audio files"""
        # Process regular audio files
        audio_files = soup.find_all('audio')
        for audio in audio_files:
            file_url = self.downloader.get_file_url(audio, ['data-trackurl', 'data-url'])
            if not file_url or not file_url.endswith('.mp3'):
                continue

            suffix = self._determine_media_type(file_url)
            filename = self.downloader.create_filename(soup.title.text, suffix, '.mp3')
            self.downloader.download_file(file_url, filename, soup.title.text, file_prefix)
        
        # Look for full episode audio in download links
        download_links = soup.find_all('a', {'download': True, 'data-trackurl': True})
        for link in download_links:
            file_url = link.get('data-trackurl')
            if file_url and file_url.lower().endswith('.mp3'):
                # Skip if it's a dialogue or review audio (already handled)
                if any(x in file_url.lower() for x in ['dialogue', 'review']):
                    continue
                filename = self.downloader.create_filename(soup.title.text, 'Full Episode', '.mp3')
                self.downloader.download_file(file_url, filename, soup.title.text, file_prefix)
                break  # Found the full episode audio, no need to check other links

    def process_video(self, soup, file_prefix):
        """Process video files"""
        video_files = soup.find_all('video')
        for video in video_files:
            file_url = self.downloader.get_file_url(video, ['data-trackurl', 'data-url'])
            if not file_url or not (file_url.endswith('.mp4') or file_url.endswith('.m4v')):
                continue

            extension = '.' + file_url.split('.')[-1]
            suffix = self._determine_media_type(file_url)
            filename = self.downloader.create_filename(soup.title.text, suffix, extension)
            self.downloader.download_file(file_url, filename, soup.title.text, file_prefix)

    def process_pdf(self, soup, file_prefix):
        """Process PDF files"""
        pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x)
        print(f"Found {len(pdf_links)} PDF links in lesson")
        pdfnum = 0
        for pdf in pdf_links:
            print(f"Processing PDF: {pdf.text}")
            pdfnum += 1
            if pdfnum > 2 or "checklist" in pdf.text.lower():
                print(f"Skipping PDF: {pdf.text}")
                continue

            file_url = self.downloader.get_file_url(pdf, ['href'])
            if not file_url:
                print(f"No URL found for PDF: {pdf.text}")
                continue

            suffix = 'Lesson Notes' if 'Lesson Notes' in pdf.text else \
                    'Lesson Transcript' if 'Lesson Transcript' in pdf.text else 'PDF'
            filename = self.downloader.create_filename(soup.title.text, suffix, '.pdf')
            self.downloader.download_file(file_url, filename, soup.title.text, file_prefix)

    def _determine_media_type(self, file_url):
        """Determine media type based on URL"""
        filename = file_url.split('/')[-1].lower()
        if 'dialog' in filename or 'dialogue' in filename:
            return 'Dialogue'
        elif 'review' in filename:
            return 'Review'
        return 'Main Lesson'

def process_lesson(session, lesson_url, file_index, source_url, prefix_digits, save_dir='.'):
    """Process a single lesson"""
    try:
        lesson_source = session.get(lesson_url)
        check_http_error(lesson_source)
        lesson_soup = BeautifulSoup(lesson_source.text, 'lxml')
        
        if check_for_captcha(lesson_soup):
            print("Lessons unavailable. Captcha required.")
            exit(1)

        processor = MediaProcessor(session, source_url, save_dir)
        file_prefix = str(file_index).zfill(prefix_digits)
        
        print(f'Processing Lesson {file_prefix} - {lesson_soup.title.text}')
        
        processor.process_audio(lesson_soup, file_prefix)
        processor.process_video(lesson_soup, file_prefix)
        processor.process_pdf(lesson_soup, file_prefix)
        
        return True

    except Exception as e:
        print(f"Error processing lesson: {e}")
        return False

    
def extract_lesson_urls(session, course_url, source_url):
    """Extract all lesson URLs from the course page"""
    try:
        course_source = session.get(course_url)
        check_http_error(course_source)
        course_soup = BeautifulSoup(course_source.text, 'lxml')
        
        if check_for_captcha(course_soup):
            print("Too many requests. Captcha required.")
            exit(1)

        lesson_urls = []
        soup_urls = course_soup.find_all('div')
        
        for u in soup_urls:
            if "class" in u.attrs and "js-pathway-context-data" in u.attrs['class']:
                obj = json.loads(u.attrs['data-collection-entities'])
                for lesson in obj:
                    if lesson['url'].startswith('/lesson/'):
                        full_url = source_url + lesson['url']
                        lesson_urls.append(full_url)
                        print("URL→" + full_url)

        print('Lessons URLs successfully listed.')
        return lesson_urls

    except Exception as e:
        print(f"Error extracting course URLs: {e}")
        return None

def find_starting_index(lesson_urls, start_url):
    """Find the index of the starting lesson URL"""
    for i, url in enumerate(lesson_urls):
        if url == start_url:
            return i
    return 0

def validate_course_url(url):
    """Validate that the URL is a lesson and not a lesson library"""
    try:
        url_split = url.split('/')
        if url_split[3] == 'lesson-library':
            raise ValueError('\nThe supplied URL is not a lesson - it is the course contents page!\n'
                           'Please click the first lesson and try that URL.')
        return True
    except Exception as e:
        print(e)
        return False

def main():
    print('Establishing a new session...')
    session = None
    UA = load_ua()
    
    # Try to load existing cookies first
    if os.path.exists(COOKIES_FILE):
        session = load_cookies()
        session.headers.update({
            'User-Agent': UA
        })
        if session:
            try:
                test_response = session.get(COURSE_URL)
                check_http_error(test_response)
                if not check_login_required(test_response.text):
                    print("Successfully authenticated using cookies")
                else:
                    print("Cookies expired, need to login again")
                    session = None
            except Exception as e:
                print(f"Error testing cookies: {e}")
                session = None

    # If no valid cookies, perform regular login
    if session is None:
        session = requests.Session()
        session.headers.update({
            'User-Agent': UA
        })
        
        try:
            print(f'Trying to login to {SOURCE_URL}')
            course_response = session.post(LOGIN_URL, data=LOGIN_DATA)
            check_http_error(course_response)
            print(f'Successfully logged in as {USERNAME}')
            save_cookies(session)
        except Exception as e:
            print(f'Login Failed: {e}')
            return
    
    if not validate_course_url(COURSE_URL):
        return

    lesson_urls = extract_lesson_urls(session, COURSE_URL, SOURCE_URL)
    if lesson_urls is None or len(lesson_urls) == 0:
        print("No lesson URLs found.")
        return
    prefix_digits = len(str(len(lesson_urls)))
    # Create organized directory structure
    # Extract course ID from URL parameter lp=xxx
    course_id = COURSE_URL.split('?lp=')[1].split('&')[0]
    course_name = f'course_{course_id}'
    downloads_dir = os.path.join('downloads', course_name)
    os.makedirs(downloads_dir, exist_ok=True)
    save_dir = downloads_dir
    
    # Find the starting index based on the provided URL
    start_index = find_starting_index(lesson_urls, COURSE_URL)
    
    # Override start_index to start from lesson 41 (0-based index 40)
    start_lesson = 40  # 41st lesson (0-based index 40)
    if start_lesson < len(lesson_urls):
        start_index = start_lesson
    
    if start_index > 0:
        print(f"Starting from lesson {start_index + 1} of {len(lesson_urls)}")
    
    for i in range(start_index, len(lesson_urls)):
        file_index = i + 1  # 1-based index for display and filenames
        file_prefix = str(file_index).zfill(prefix_digits)
        lesson_url = lesson_urls[i]
        
        # Skip if the lesson directory already exists and has files
        lesson_dir = os.path.join(save_dir, file_prefix)
        if os.path.exists(lesson_dir) and os.listdir(lesson_dir):
            print(f'Skipping lesson {file_index} (already downloaded)')
            continue
            
        if process_lesson(session, lesson_url, file_index, SOURCE_URL, prefix_digits, save_dir):
            if i + 1 < len(lesson_urls):
                wait = randint(110, 300)
                print(f'Pausing {wait}s before scraping next lesson...\n')
                time.sleep(wait)
        else:
            break

    print('Yatta! Finished downloading the course~')

main()