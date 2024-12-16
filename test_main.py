import os
import pytest
from unittest.mock import MagicMock
from scrapy.http import HtmlResponse, Request
from main import TripComSpider, setup_database, save_to_database, Property

@pytest.fixture
def mock_session():
    """Set up a mock database session."""
    session = MagicMock()
    return session

@pytest.fixture
def spider():
    """Create an instance of the TripComSpider."""
    return TripComSpider()

def test_parse(spider):
    """Test the parse method of the spider."""
    html = """
    <html>
        <body>
            <script>
                window.IBU_HOTEL = {"initData": {"htlsData": {"inboundCities": [{"name": "City1", "id": "1"}], "outboundCities": []}}};
            </script>
        </body>
    </html>
    """
    response = HtmlResponse(url='https://uk.trip.com/hotels/?locale=en-GB&curr=GBP', body=html, encoding='utf-8')
    results = list(spider.parse(response))
    assert len(results) == 1
    assert isinstance(results[0], Request)
    assert 'city=1' in results[0].url

def test_parse_city_hotels(spider):
    """Test the parse_city_hotels method of the spider."""
    html = """
    <html>
        <body>
            <script>
                window.IBU_HOTEL = {"initData": {"firstPageList": {"hotelList": [
                    {"hotelBasicInfo": {"hotelId": "123", "hotelName": "Hotel A", "hotelImg": "http://example.com/image.jpg", "price": "100"},
                     "commentInfo": {"commentScore": 4.5},
                     "positionInfo": {"positionName": "Location A", "coordinate": {"lat": 51.5074, "lng": -0.1278}},
                     "roomInfo": {"physicalRoomName": "Deluxe Room"}
                    }
                ]}}};
            </script>
        </body>
    </html>
    """
    response = HtmlResponse(url='https://uk.trip.com/hotels/list?city=1', body=html, encoding='utf-8')
    response.meta['city_name'] = 'City1'
    results = list(spider.parse_city_hotels(response))
    assert len(results) == 1
    hotel = results[0]
    assert hotel['title'] == 'Hotel A'
    assert hotel['rating'] == 4.5
    assert hotel['latitude'] == 51.5074
    assert hotel['longitude'] == -0.1278
    assert hotel['price'] == '100'

def test_save_to_database(mock_session):
    """Test saving data to the database."""
    data = {
        "title": "Hotel Test",
        "rating": 4.5,
        "location": "Test Location",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "room_type": "Deluxe",
        "price": 100,
        "image_path": "path/to/image.jpg"
    }
    save_to_database(data, mock_session)
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    saved_property = mock_session.add.call_args[0][0]
    assert isinstance(saved_property, Property)
    assert saved_property.title == "Hotel Test"

def test_database_setup():
    """Test database setup."""
    session = setup_database()
    assert session is not None
