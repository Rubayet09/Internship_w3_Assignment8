from sqlalchemy import create_engine, text

# Create the engine and connect
engine = create_engine('postgresql+psycopg2://myuser:ulala@localhost:5432/tripcom_db')
connection = engine.connect()

print("Connected successfully!")

# Query to fetch all entries from the properties table
result = connection.execute(text("SELECT * FROM properties;"))

# Fetch and print all rows from the table
properties = result.fetchall()
for row in properties:
    print(row)

# Close the connection
connection.close()
