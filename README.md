# Installing Postgresql
1. If not installed, use Homebrew:
    ```bash
    Copy code
    brew install postgresql```

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
# Installing uv & running the project.
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

