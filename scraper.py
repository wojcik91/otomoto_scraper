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
    if(soup):
        next_button = soup.find('ul', class_='om-pager').find('li', class_='next abs')
        if(next_button):
            next_url = next_button.a['href']
        else:
            next_url = None
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

    engine = create_engine('sqlite:///otomoto.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    # put every listing found in a queue
    page_counter = 1
    while(page_url):
        print(f"Processing page #{page_counter}...")
        soup = get_page_soup(page_url)
        offer_list = get_all_listings(soup)
        print(f'Found {len(offer_list)} listings in page #{page_counter}...')
        for offer in offer_list:
            q.put(offer)
        print(f'Current queue size: {q.qsize()}')
        # go through every listing and insert data into the database
        queue_size = q.qsize()
        listing_counter = 1
        while(not q.empty()):
            print(f'Processing listing {listing_counter}/{queue_size} on page #{page_counter}...')
            listing = q.get()
            try:
                (id, brand, model, year, mileage, engine_capacity, fuel_type, price) = get_car_data(listing)
            except ValueError as e:
                print(e.args)
                continue
            except IndexError as ie:
                print(ie.args)
                continue
                
            if(session.query(Listing).filter_by(id=id).first()):
                print('Listing already in the database...')
            else:
                car = Listing(id=id, brand=brand, model=model, year=year, mileage=mileage, engine_capacity=engine_capacity, fuel_type=fuel_type, price=price)
                session.add(car)
                session.commit()
            listing_counter += 1

        page_url = get_next_page_url(soup)
        page_counter += 1
        sleep(0.1)

    session.close()
