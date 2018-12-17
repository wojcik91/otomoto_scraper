from bs4 import BeautifulSoup
import requests
from time import sleep
import queue

ENTRYPOINT_URL = "https://www.otomoto.pl/osobowe/toyota/auris/?search%5Bbrand_program_id%5D%5B0%5D=&search%5Bcountry%5D=&page=53"


def get_page_soup(url):
    response = requests.get(url)
    page_soup = BeautifulSoup(response.text, 'html.parser')
    return page_soup


def get_next_page_url(soup):
    next_button = soup.find('ul', class_='om-pager').find('li', class_='next abs')
    if(next_button):
        next_url = next_button.a['href']
    else:
        next_url = None
    return next_url


def get_all_listings(soup):
    listings = soup.find_all('article', class_='adListingItem')
    return listings


if __name__ == "__main__":
    page_url = ENTRYPOINT_URL
    q = queue.SimpleQueue()

    # put every listing found in a queue
    while(page_url):
        soup = get_page_soup(page_url)
        offer_list = get_all_listings(soup)
        for offer in offer_list:
            q.put(offer)
        page_url = get_next_page_url(soup)
        sleep(0.1)
