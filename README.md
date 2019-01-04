# otomoto_scraper
Web scraper for downloading listings from otomoto.pl. I made it because I'm trying to sell my car and wanted to know how much it's actually worth. The script goes through the site page by page and inserts listings into an SQLite database for further processing.

## Warning

Running this script for a sufficiently large number of pages will get your IP banned for 24 hours. I couldn't find otomoto's request limit in their ToS, so I set the timeout between HTTP requests at 0.1s.

## Built With

* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - Used to navigate and parse HTML contend of web pages
* [Requests](http://docs.python-requests.org/en/master/) - Used to make HTTP requests
* [SQLAlchemy](https://www.sqlalchemy.org/) - Database toolkit and ORM to interact with the SQLite DB
