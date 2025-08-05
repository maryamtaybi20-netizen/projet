import psycopg2

conn = psycopg2.connect(
    dbname="bus_traffic_stats",
    user="postgres",
    password="2006",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Création des tables
cur.execute("""
CREATE TABLE bus (
    id_bus SERIAL PRIMARY KEY,
    bus_number VARCHAR(20) NOT NULL,
    capacity INT
);
""")

cur.execute("""
CREATE TABLE bus_line (
    id_line SERIAL PRIMARY KEY,
    line_number VARCHAR(10) UNIQUE NOT NULL,
    line_name VARCHAR(255) NOT NULL,
    origin VARCHAR(255),
    destination VARCHAR(255),
    distance_km FLOAT
);
""")

cur.execute("""
CREATE TABLE stop (
    id_stop SERIAL PRIMARY KEY,
    stop_name VARCHAR(100) NOT NULL,
    latitude FLOAT,
    longitude FLOAT,
    zone VARCHAR(100)    
);
""")

cur.execute("""
CREATE TABLE trip (
    id_trip SERIAL PRIMARY KEY,
    id_bus INT REFERENCES bus(id_bus),
    line_number VARCHAR(10),
    line_name VARCHAR(255),
    origin VARCHAR(255),
    destination VARCHAR(255),
    distance_km FLOAT,
    start_datetime TIMESTAMP,
    end_datetime TIMESTAMP,
    driver_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Terminé'
);
""")

cur.execute("""
CREATE TABLE trip_stop (
    id_trip_stop SERIAL PRIMARY KEY,
    id_trip INT REFERENCES trip(id_trip),
    id_stop INT REFERENCES stop(id_stop),
    stop_time TIME,
    passenger_count INT
);
""")   

conn.commit()
cur.close()
conn.close()

print("Base, tables créées avec succès.")
