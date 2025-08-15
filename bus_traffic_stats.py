import psycopg2
from datetime import datetime

# Database connection details
conn = psycopg2.connect(
    dbname="bus_traffic_stats",
    user="postgres",
    password="2006",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Dropping existing tables to allow for clean re-creation
# This is useful for development to avoid "table already exists" errors
cur.execute("DROP TABLE IF EXISTS trip, bus, stop, bus_line;")


# Create the 'bus' table
cur.execute("""
CREATE TABLE bus (
    id_bus SERIAL PRIMARY KEY,
    bus_number VARCHAR(50) NOT NULL UNIQUE,
    capacity INT,
    matricule VARCHAR(50) UNIQUE
);
""")

# Create the 'bus_line' table
# This was missing in your original code but referenced in 'trip'
cur.execute("""
CREATE TABLE bus_line (
    id_line SERIAL PRIMARY KEY,
    line_number VARCHAR(50) NOT NULL UNIQUE,
    line_name VARCHAR(255),
    origin VARCHAR(255),
    destination VARCHAR(255),
    distance_km FLOAT
);
""")

# Create the 'stop' table
cur.execute("""
CREATE TABLE stop (
    id_stop SERIAL PRIMARY KEY,
    stop_name VARCHAR(100) NOT NULL UNIQUE,
    latitude FLOAT,
    longitude FLOAT,
    zone VARCHAR(100)
);
""")

# Create the 'trip' table
# Corrected 'id_line' to reference 'bus_line' and fixed data types
# Removed duplicate table creation and added missing columns for the INSERT statement
cur.execute("""
CREATE TABLE trip (
    id_trip SERIAL PRIMARY KEY,
    id_bus INT REFERENCES bus(id_bus) ON DELETE RESTRICT,
    id_line INT REFERENCES bus_line(id_line) ON DELETE RESTRICT,
    driver_name VARCHAR(100),
    start_datetime TIMESTAMP,
    end_datetime TIMESTAMP,
    passenger_count INT,
    status VARCHAR(50) DEFAULT 'Terminé',
    stop_time TIME
);
""")

# Commit changes to the database
conn.commit()
print("Base de données et tables créées et remplies avec succès.")

# Close the cursor and connection
cur.close()
conn.close()

