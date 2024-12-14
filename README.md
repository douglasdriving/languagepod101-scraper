<h1 align="center">:zap: languagepod101-scraper	:zap:</h1>
<p align="center">
  <img src="readme\language_selection.jpg" alt="Language selection">
  <br>
  <i>languagepod101-scraper is a resource for dozen of language learning courses and study material for FREE.</i>
</p>
<hr>

## :mortar_board: About

languagepod101-scraper helps you download full language courses and save them to a local directory.
The courses are produced and distributed by [Innovative Language](https://www.innovativelanguage.com/online-language-courses),
who provides language learning courses from a selection of dozens of languages. Each lesson is usually 10-20 minutes long.

To get started, [choose one of the languages courses](https://www.innovativelanguage.com/online-language-courses)
offered by Innovative Language and create a free account.

## :pushpin: Usage

To use the script, fulfill the requirements and follow the example as demonstrated below.

### :electric_plug: Requirements

- Download and install [Python 3.9+](https://www.python.org/).
- Install required packages from [requirements.txt](requirements.txt) file using
  [pip](https://packaging.python.org/tutorials/installing-packages/).

  ```sh
  pip install -r requirements.txt
  ```

### :bookmark_tabs: Example

For the sake of example, the process of downloading of a course from
[Japanese Pod 101](https://www.japanesepod101.com/) will be demonstrated.

Japanese Pod 101 and all other sites have a similar structure which looks as following:

  ```
  Japanesepod101
  ├─ Level 1 - Absolute Beginner
  │  ├─ Newbie Season 1
  │  │  ├─ lesson 01
  │  │  ├─ lesson 02
  │  │  ├─ lesson 03
  │  │  ├─ ...
  │  ├─ Newbie Season 2
  │  ├─ ...
  ├─ Level 2 - Beginner
  │  ├─ Lower Beginner Season 1
  │  │  ├─ lesson 01
  │  │  ├─ lesson 02
  │  │  ├─ lesson 03
  │  │  ├─ ...
  │  ├─ ...
  ├─ Level 3 - Intermediate
  │  ├─ ...
  │  │  ├─ ...
  │  │  ├─ ...
  │  ├─ ...
  │  ├─ ...
  ├─ Level 4 - Upper Intermediate
  │  ├─ ...
  ├─ Level 5 - Advanced
  │  ├─ ...
  ```

- To download *Lower Beginner Season 1* we will have to use our web browser to navigate
  to `lesson 1` of this course (any other lesson url from the **same course** is ok too...).

  Navigation would look like this: `Japanesepod101` → `Level 2 - Beginner` → `Lower Beginner Season 1` → `lesson 01`.
  
  Save the URL for `lesson 01` from the address bar, as you will have to provide it to the script later on.

- Create a directory in your PC for this course, and enter into it.

- Run the [language101_scraper.py](language101_scraper.py) script, and follow the instructions.
  You will have to provide:

  - the email you used to sign up for the course
  - your password for the course
  - the course's lesson URL you have navigated through earlier
    (in our example: `lesson 01` of the `Lower Beginner Season 1` course).

- Alternatively, you can pass the data as parameters when invoking the script:

  ```sh
  ./language101_scraper.py -u $USERNAME -p $PASSWORD --url YOUR_LESSON_URL
  ```

- The script will start downloading the MP3/MP4/M4V files into the local navigated folder.
  Any possible errors would be printed out.

- Output inside folder should look like this:

  ```
  ├─01 - A Formal Japanese Introduction - JapanesePod101 - Dialogue.mp3
  ├─01 - A Formal Japanese Introduction - JapanesePod101 - Review.mp3
  ├─01 - A Formal Japanese Introduction - JapanesePod101 - Main Lesson.mp3
  ├─02 - Which Famous Tokyo Tower is That - JapanesePod101 - Dialogue.mp3
  ├─02 - Which Famous Tokyo Tower is That - JapanesePod101 - Main Lesson.mp3
  ├─02 - Which Famous Tokyo Tower is That - JapanesePod101 - Review.mp3
  ├─03 - Networking in Japan - JapanesePod101 - Dialogue.mp3
  ├─03 - Networking in Japan - JapanesePod101 - Main Lesson.mp3
  ├─03 - Networking in Japan - JapanesePod101 - Review.mp3
  ├─...
  ```

## :clipboard: Disclaimer and known issues

- Any usage of the script is under user's responsibility only. Users of the script must act according to site's terms.

- As of today, Innovative Language's terms of use does not forbid usage of crawlers or scrapers on any of their sites.
This may change in the future, so be aware.

- If you like the services Innovative Language provides you should consider a monthly subscription. Basic programs start at around $5 per month and include support from native speaker teachers.

- As with all websites, the site's structure may change in the future and thus, as often happens with scraping scripts, deprecate it. It is not really a question of *if* the site's source code will change but rather **when** (so enjoy it while it's still working :grin:).

## :lock: License

All of the content presented in the websites belongs to the original creators (Innovative Language) and I have nothing to do with it.

The license below refers only to the script and not to the downloaded content.

[License - MIT](LICENSE.md)

## :speech_balloon: Status and changelog

- **14.12.2024**
  [@BenoitAnastay](https://github.com/BenoitAnastay) and [tassa-yoniso-manasi-karoto]([) ](https://github.com/tassa-yoniso-manasi-karoto) created mor modular code and downloading specific lessons. You need to subscribe for premium if you wnat to download advanced material.

  Also, now you will be prompted to have a captcha every now and then, the script will not attempt to circuvment it in any way.

  As mentioned before, if you do enjoy the service langpod guys give you, pay them!

  The updates:
  -modular functions
- ***require the user to provide the User Agent of his browser in the ua.txt file before running the script***
- PDFs support
- try to auth using cookies from a Netscape cookies.txt: you can use [cookies exported from your browser](https://github.com/hrdl-github/cookies-txt), this can help mitigate Captchas
- reworked scraping: longer sleeping and Captcha detection


- **23.03.2022**:
Added support for basic video downloading (nothing fancy, just m4v and mp4 files)
Added error handling for when a lesson library/lesson contents URL is used instead of the first lesson (user is now warned)
- **11.05.2021**:
Headers and waiting time added, script is alive again.
