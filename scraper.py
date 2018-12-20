from bs4 import BeautifulSoup
import requests
from time import sleep
import queue
from sqlalchemy import create_engine
from models import Listing
from sqlalchemy.orm import sessionmaker

ENTRYPOINT_URL = "https://www.otomoto.pl/osobowe/toyota/auris/?search%5Bbrand_program_id%5D%5B0%5D=&search%5Bcountry%5D=&page=1"


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


def get_car_data(listing):
    id = int(listing['data-ad-id'])
    title = listing.find('a', class_='offer-title__link')['title']
    brand = title.split(' ')[0]
    model = title.split(' ')[1]
    try:
        year = int(listing.find(attrs={'data-code': 'year'}).span.string)
        mileage_string = listing.find(attrs={'data-code': 'mileage'}).span.string.split(' ')
        mileage = int(''.join(mileage_string[:-1]))
        engine_capacity_string = listing.find(attrs={'data-code': 'engine_capacity'}).span.string.split(' ')
        engine_capacity = int(''.join(engine_capacity_string[:-1]))
        fuel_type = listing.find(attrs={'data-code': 'fuel_type'}).span.string
    except(AttributeError):
        raise ValueError(f'Incomplete data for ID={id}. Discarding listing...') 
    price_string = listing.find('span', class_='offer-price__number').text.split(' ')
    price = int(''.join(price_string[:-1]).replace(',', '.'))
    return (id, brand, model, year, mileage, engine_capacity, fuel_type, price)


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

    engine = create_engine('sqlite:///otomoto.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    # go through every listing and insert data into the database
    while(not q.empty()):
        listing = q.get()
        try:
            (id, brand, model, year, mileage, engine_capacity, fuel_type, price) = get_car_data(listing)
        except ValueError as e:
            print(e.args)
            continue
        car = Listing(id=id, brand=brand, model=model, year=year, mileage=mileage, engine_capacity=engine_capacity, fuel_type=fuel_type, price=price)
        session.add(car)
    session.commit()
    session.close()
