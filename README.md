# otomoto_scraper
Web scraper for downloading listings from otomoto.pl. I made it because I'm trying to sell my car and wanted to know how much it's actually worth. The script goes through the site page by page and inserts listings into an SQLite database for further processing.
## Prerequisites

You should start by visiting otomoto.pl and using their filtering tools to narrow down which cars you want to download. Then use the generated URL as an entrypoint for the script. For example the URL for all available Toyotas is:

```
https://www.otomoto.pl/osobowe/toyota/?search%5Bbrand_program_id%5D%5B0%5D=&search%5Bcountry%5D=
```

The scraper uses links at the bottom of the page to find the next one and repeats the process until it reaches the end.

## Installation

The script itself is pure Python, so it doesn't require any installation. Just create a virtual environment:

```bash
python3 -m venv env
```

Then install dependencies:

```bash
pip install -r requirements.txt
```

Before running the scraper for the first time you have to initialize a local SQLite database:

```bash
python db_create.py
```

## Usage

Activate your virtual environment:

```bash
source env/bin/activate
```

Then simply run the scraper:

```bash
python scraper.py
```

## Warning

Running this script for a sufficiently large number of pages will get your IP banned for 24 hours. I couldn't find otomoto's request limit in their ToS, so I set the timeout between HTTP requests at 0.1s.

## Built With

* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - Used to navigate and parse HTML contend of web pages
* [Requests](http://docs.python-requests.org/en/master/) - Used to make HTTP requests
* [SQLAlchemy](https://www.sqlalchemy.org/) - Database toolkit and ORM to interact with the SQLite DB
