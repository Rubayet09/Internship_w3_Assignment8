
## Internship_w3_Assignment8


# Scrape Property Info into Postgres database Internship Project A8

## Table of Contents 
1. [Overview](#overview) 
2. [Key Features](#key-features) 
3.  [Technologies Used](#technologies-used) 
5. [Development Setup](#development-setup) 
6. [Project Structure](#project-structure) 
7. [Author](#author)


## Overview
This a project where scrapy spider have been used to scrape data from a website: https://uk.trip.com/hotels/?locale=en-GB&curr=GBP and store them into postgres database. The project also involves code coverage testing.

## Key Features 
- **Scraping Data**: Scraping the data from website, the property details of all the hotels among all the cities  get scraped.
- **Selected Data**: Among all the cities, random 3 cities get selected and stores their hotel details.
 - **Postgres Table**: The selected data can be seen in the postgres table.


## Technologies Used

- **Framework**: Scrapy
- **Database**: Postgres with SqlAlchemy
- **Testing**: Python `unittest` 


## Development Setup

### Prerequisites

Ensure the following are installed on your system:

- Python 3.10 or higher
- Scrapy
- PostgreSQL with SqlAlchemy extension 


### Installing PostgreSQL
1. If not installed, use Homebrew:
    ```bash
    sudo apt-get install build-essential procps curl file git

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    brew install postgresql
    ```

2. After installation, create the myuser using the following commands,
    ```bash
    psql postgres
    CREATE DATABASE tripcom_db;
    CREATE USER myuser WITH PASSWORD 'ulala';
    GRANT ALL PRIVILEGES ON DATABASE tripcom_db TO myuser;
    GRANT ALL PRIVILEGES ON DATABASE tripcom_db TO myuser;
    \q
    ```
3. Verify the installation with the following python script
    ```python 
    from sqlalchemy import create_engine
    engine = create_engine('postgresql+psycopg2://myuser:mypassword@localhost:5432/tripcom_db')
    connection = engine.connect()
    print("Connected successfully!")
    connection.close()
    ```
## Installing uv & running the project.
Please intsall uv to create the virtual environemnt.

```bash    
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Please navigate to the root folder of the project. Now, run the following commands to generate the python environment.
```bash
uv sync
```

Now run the following command to run the project.

```bash
uv run python main.py
```

Database state view

To see the current state of the database, please run the `database.py`  file, using the following command.

```bash 
uv run python database.py
```

Code coverage test

To run the code coverage please run the following command.
```bash
uv run pytest test_main.py --cov=main --cov-report=term-missing
```

## Author

Rubayet Shareen
SWE Intern, W3 Engineers
Dhaka, Bangladesh
