import os
import json
import pytest
from unittest.mock import patch, MagicMock, mock_open
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import setup_database, save_to_database, save_to_json, Property, TripComSpider
from scrapy.http import HtmlResponse, Request
import shutil


@pytest.fixture(scope="module")
def test_database():
    """Set up a test database."""
    engine = create_engine('sqlite:///:memory:')  # Use SQLite in-memory database
    session = setup_database()
    yield session
    engine.dispose()

@pytest.fixture
def mock_json_file(tmp_path):
    """Create a temporary JSON file for testing."""
    test_json_file = tmp_path / "test_hotels.json"
    return str(test_json_file)

@pytest.fixture
def mock_image_dir(tmp_path):
    """Create a temporary directory for hotel images."""
    image_dir = tmp_path / "hotel_images"
    image_dir.mkdir()
    return str(image_dir)



def test_save_to_database(test_database):
    """Test saving a property to the database."""
    session = test_database
    test_data = {
        "title": "Test Hotel",
        "rating": 4.5,
        "location": "Test City",
        "latitude": 12.3456,
        "longitude": 78.9012,
        "room_type": "Deluxe Room",
        "price": 123.45,
        "image_path": "path/to/image.jpg"
    }

    # Clear database before running the test
    session.query(Property).delete()
    session.commit()

    save_to_database(test_data, session)

    # Check if the property was added
    result = session.query(Property).first()
    assert result is not None
    assert result.title == "Test Hotel"
    assert result.rating == 4.5
    assert result.location == "Test City"

def test_save_to_json(mock_json_file):
    """Test saving hotel data to a JSON file."""
    test_data = {
        "title": "Test Hotel JSON",
        "rating": 4.2,
        "location": "Test JSON Location"
    }
    save_to_json(test_data, mock_json_file)

    # Verify the JSON content
    with open(mock_json_file, 'r') as f:
        content = f.readlines()
    assert len(content) == 1
    assert json.loads(content[0])["title"] == "Test Hotel JSON"



@patch("main.TripComSpider.logger", new_callable=MagicMock)
def test_tripcom_spider_initial_parse(mock_logger, mock_json_file):
    """Test the initial parse method of TripComSpider."""
    # Create a mock Scrapy response
    spider = TripComSpider(session=None, json_file=mock_json_file)
    html_content = """
    <html>
        <head>
            <script>
                window.IBU_HOTEL = {
                    "initData": {
                        "htlsData": {
                            "inboundCities": [{"name": "City 1", "id": "101"}, {"name": "City 2", "id": "102"}],
                            "outboundCities": [{"name": "City 3", "id": "103"}]
                        }
                    }
                };
            </script>
        </head>
    </html>
    """
    request = Request(url="https://uk.trip.com/hotels/")
    response = HtmlResponse(url=request.url, body=html_content, encoding='utf-8')

    # Call parse
    result = list(spider.parse(response))
    assert len(result) == 3  # 3 cities randomly selected
    assert "City" in result[0].meta['city_name']

@patch("main.TripComSpider.logger", new_callable=MagicMock)
def test_tripcom_spider_parse_city_hotels(mock_logger, mock_json_file):
    """Test parsing city hotels logic."""
    spider = TripComSpider(session=None, json_file=mock_json_file)
    html_content = """
    <html>
        <head>
            <script>
                window.IBU_HOTEL = {
                    "initData": {
                        "firstPageList": {
                            "hotelList": [
                                {
                                    "hotelBasicInfo": {"hotelId": "123", "hotelName": "Test Hotel 1", "hotelImg": "http://example.com/img1.jpg", "price": 100},
                                    "positionInfo": {"positionName": "Test Location", "coordinate": {"lat": 10.0, "lng": 20.0}},
                                    "commentInfo": {"commentScore": 4.5},
                                    "roomInfo": {"physicalRoomName": "Deluxe"}
                                }
                            ]
                        },
                        "pagination": {"nextPage": null}
                    }
                };
            </script>
        </head>
    </html>
    """
    request = Request(url="https://uk.trip.com/hotels/list")
    response = HtmlResponse(url=request.url, body=html_content, encoding='utf-8')

    spider.parse_city_hotels(response)

    # Verify JSON file was written
    with open(mock_json_file, 'r') as f:
        content = f.readlines()
    assert len(content) == 1
    assert "Test Hotel 1" in content[0]


if __name__ == "__main__":
    pytest.main(["--cov=main", "--cov-report=term-missing"])
