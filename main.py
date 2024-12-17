import os
import scrapy
import json
import re
import requests
from scrapy.crawler import CrawlerProcess
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random  

# Database ORM setup
Base = declarative_base()

class Property(Base):
    __tablename__ = 'properties'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    rating = Column(Float, nullable=True)
    location = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    room_type = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    image_path = Column(String, nullable=True)

def setup_database():
    """Database connection setup"""
    engine = create_engine('postgresql+psycopg2://myuser:ulala@localhost:5432/tripcom_db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def save_to_database(data, session):
    """Save hotel data to PostgreSQL database"""
    property_entry = Property(**data)
    session.add(property_entry)
    session.commit()

def save_to_json(data, json_file):
    """Save hotel data to JSON file"""
    with open(json_file, 'a') as f:
        f.write(json.dumps(data) + "\n")

class TripComSpider(scrapy.Spider):
    name = "tripCrawler"
    allowed_domains = ["uk.trip.com"]
    start_urls = ["https://uk.trip.com/hotels/?locale=en-GB&curr=GBP"]

    def __init__(self, session, json_file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session
        self.json_file = json_file

    def parse(self, response):
        """Extract city list and randomly select 3 cities"""
        script_data = response.xpath("//script[contains(text(), 'window.IBU_HOTEL')]/text()").get()
        if script_data:
            match = re.search(r"window\.IBU_HOTEL\s*=\s*(\{.*?\});", script_data, re.DOTALL)
            if match:
                try:
                    ibu_hotel_data = json.loads(match.group(1))
                    inbound_cities = ibu_hotel_data.get("initData", {}).get("htlsData", {}).get("inboundCities", [])
                    outbound_cities = ibu_hotel_data.get("initData", {}).get("htlsData", {}).get("outboundCities", [])

                    all_cities = [city for group in [inbound_cities, outbound_cities] for city in group]
                    selected_cities = random.sample(all_cities, min(3, len(all_cities)))  # Randomly pick up to 3 cities

                    self.logger.info(f"Selected cities: {[city.get('name') for city in selected_cities]}")

                    for city in selected_cities:
                        city_name = city.get("name", "Unknown")
                        city_id = city.get("id", "")

                        if city_id:
                            hotels_url = f"https://uk.trip.com/hotels/list?city={city_id}&page=1"
                            yield scrapy.Request(
                                url=hotels_url,
                                callback=self.parse_city_hotels,
                                meta={'city_name': city_name, 'city_id': city_id, 'page': 1}
                            )
                except json.JSONDecodeError:
                    self.logger.error("Failed to parse city data JSON")
                except Exception as e:
                    self.logger.error(f"Unexpected error: {e}")

    def parse_city_hotels(self, response):
        """Parse hotels in a city and save details"""
        city_name = response.meta.get('city_name', 'Unknown')
        page = response.meta.get('page', 1)
        city_id = response.meta.get('city_id')

        images_dir = os.path.join(os.getcwd(), 'hotel_images', city_name.lower().replace(' ', '_'))
        os.makedirs(images_dir, exist_ok=True)

        script_data = response.xpath("//script[contains(text(), 'window.IBU_HOTEL')]/text()").get()
        if script_data:
            match = re.search(r"window\.IBU_HOTEL\s*=\s*(\{.*?\});", script_data, re.DOTALL)
            if match:
                try:
                    ibu_hotel_data = json.loads(match.group(1))
                    hotel_list = ibu_hotel_data.get("initData", {}).get("firstPageList", {}).get("hotelList", [])
                    next_page = ibu_hotel_data.get("initData", {}).get("pagination", {}).get("nextPage")

                    for hotel in hotel_list:
                        hotel_basic = hotel.get("hotelBasicInfo", {})
                        position_info = hotel.get("positionInfo", {})
                        comment_info = hotel.get("commentInfo", {})
                        room_info = hotel.get("roomInfo", {})

                        hotel_id = hotel_basic.get("hotelId", "")
                        hotel_name = hotel_basic.get("hotelName", "").replace(" ", "_")
                        image_url = hotel_basic.get("hotelImg", "")

                        property_data = {
                            "title": hotel_basic.get("hotelName", ""),
                            "rating": comment_info.get("commentScore", None),
                            "location": position_info.get("positionName", ""),
                            "latitude": position_info.get("coordinate", {}).get("lat", None),
                            "longitude": position_info.get("coordinate", {}).get("lng", None),
                            "room_type": room_info.get("physicalRoomName", None),
                            "price": hotel_basic.get("price", None),
                            "image_path": None
                        }

                        if image_url:
                            try:
                                image_filename = f"{hotel_id}_{hotel_name}.jpg"
                                image_path = os.path.join(images_dir, image_filename)
                                response_img = requests.get(image_url)

                                if response_img.status_code == 200:
                                    with open(image_path, 'wb') as f:
                                        f.write(response_img.content)
                                    property_data['image_path'] = os.path.relpath(image_path)
                                else:
                                    self.logger.warning(f"Failed to download image for {hotel_name}")
                            except Exception as e:
                                self.logger.error(f"Image download error: {e}")

                        save_to_database(property_data, self.session)
                        save_to_json(property_data, self.json_file)

                    # Handle pagination
                    if next_page:
                        next_page_url = f"https://uk.trip.com/hotels/list?city={city_id}&page={page + 1}"
                        yield scrapy.Request(
                            url=next_page_url,
                            callback=self.parse_city_hotels,
                            meta={'city_name': city_name, 'city_id': city_id, 'page': page + 1}
                        )
                except json.JSONDecodeError:
                    self.logger.error("Failed to parse hotel list JSON")
                except Exception as e:
                    self.logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    session = setup_database()
    json_file = "hotels_data.json"

    # Clear JSON file before running
    open(json_file, 'w').close()

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    })
    process.crawl(TripComSpider, session=session, json_file=json_file)
    process.start()
