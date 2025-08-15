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

# Inserting data into the 'bus' table
cur.execute("""
INSERT INTO bus (bus_number, capacity, matricule) VALUES
('BUS001', 100, '1234-AB-01'), ('BUS002', 100, '1234-AB-02'),
('BUS003', 100, '1234-AB-03'), ('BUS004', 100, '1234-AB-04'),
('BUS005', 100, '1234-AB-05'), ('BUS006', 100, '1234-AB-06'),
('BUS007', 100, '1234-AB-07'), ('BUS008', 100, '1234-AB-08'),
('BUS009', 100, '1234-AB-09'), ('BUS010', 100, '1234-AB-10'),
('BUS011', 100, '1234-AB-11'), ('BUS012', 100, '1234-AB-12'),
('BUS013', 100, '1234-AB-13'), ('BUS014', 100, '1234-AB-14'),
('BUS015', 100, '1234-AB-15'), ('BUS016', 100, '1234-AB-16'),
('BUS017', 100, '1234-AB-17'), ('BUS018', 100, '1234-AB-18'),
('BUS019', 100, '1234-AB-19'), ('BUS020', 100, '1234-AB-20'),
('BUS021', 100, '1234-AB-21'), ('BUS022', 100, '1234-AB-22'),
('BUS023', 100, '1234-AB-23'), ('BUS024', 100, '1234-AB-24'),
('BUS025', 100, '1234-AB-25'), ('BUS026', 100, '1234-AB-26'),
('BUS027', 100, '1234-AB-27'), ('BUS028', 100, '1234-AB-28'),
('BUS029', 100, '1234-AB-29'), ('BUS030', 100, '1234-AB-30'),
('BUS031', 100, '1234-AB-31'), ('BUS032', 100, '1234-AB-32'),
('BUS033', 100, '1234-AB-33'), ('BUS034', 100, '1234-AB-34'),
('BUS035', 100, '1234-AB-35'), ('BUS036', 100, '1234-AB-36'),
('BUS037', 100, '1234-AB-37'), ('BUS038', 100, '1234-AB-38'),
('BUS039', 100, '1234-AB-39'), ('BUS040', 100, '1234-AB-40');
""")

# Inserting data into the 'bus_line' table
# This table needs to be populated before the 'trip' table because 'trip' references its ID
cur.execute("""
INSERT INTO bus_line (line_number, line_name, origin, destination, distance_km) VALUES
('L1', 'MOUQUAOUAMA SUD INBIAT - HOPITAL HASSAN II', 'Mouquaouama Sud Inbiaat', 'Terminus hôpital Hassan II V', 12.5),
('L2', 'P.E VALLEE DES OISEAUX - HAY MOHAMMEDI', 'P.E. Vallée des oiseaux', 'Ait El Mouden Terminus', 10.0),
('L3', 'P.E VALLEE DES OISEAUX - ELHOUDA', 'P.E. Vallée des oiseaux', 'Houda Terminus', 8.5),
('L5', 'P.E VALLEE DES OISEAUX - DRARGA', 'P.E. Vallée des oiseaux', 'Drarga Iguerer', 15.0),
('L6', 'FACULTE - MESDOURA', 'Fac De Lettres', 'Terminus Masdoura', 9.0),
('L8', 'SODISMA - TADDART', 'Sodisma V', 'Taddart 3', 7.0),
('L9', 'JIHADIA SOUK INEZGANE - DRARGA', 'Jihadia-Souk Inezgane', 'Drarga Iguerer', 14.0),
('L10', 'INEZGANE - LAKHCHICHAT', 'Jihadia-Souk Inezgane V', 'Piscine Bourj', 8.0),
('L11', 'P.E VALLEE DES OISEAUX - POSTE INEZGANE MESDOURA', 'P.E. Vallée des oiseaux', 'Poste Inezgane Mesdoura', 11.0),
('L12', 'MARINA - AIT MELLOUL', 'MARINA V', 'Marbre Amenou', 5.0),
('L13', 'JIHADIA SOUK INEZGANE - ARGANA', 'Jihadia-Souk Inezgane', 'Argana Souk', 6.5),
('L14', 'JIHADIA SOUK INEZGANE - KASBAH TAHAR', 'Jihadia-Souk Inezgane', 'Kasbah 1 V', 4.5),
('L15', 'TILILA - POSTE INZEGANE', 'Jihadia-Souk Inezgane V', 'Tilila-L''Khawarizmi V', 3.5),
('L16', 'P.E VALLEE DES OISEAUX - ADRAR', 'P.E. Vallée des oiseaux', 'Adrar Terminus', 11.0),
('L20', 'PLACE INEZGANE - SOUK PRINCIPAL KOLEA', 'Place Inezgane', 'Complexe Commercial Ain', 9.0),
('L21', 'PLACE INEZGANE - KOLEA', 'Bachaouia', 'Winxo kolea V', 5.0),
('L22', 'P.E VALLEE DES OISEAUX - EL HAJEB TIKIOUINE', 'P.E. Vallée des oiseaux', 'El Hajeb Marche Municipal', 10.0),
('L23', 'PLACE INZGANE - LAMZAR', 'Place Inezgane', 'Lamzar Mosquee', 6.0),
('L24', 'KASBAH AGADIR OUFELLA', 'Pied Oufela Agadir', 'Agadir Kasbah Oufela', 8.0),
('L26', 'P.E VALLEE DES OISEAUX - WIFAQ - PLACE INEZGANE', 'P.E. Vallée des oiseaux', 'Place Inezgane V', 12.0),
('L27', 'BARREAU - TERMINUS AGHROUD', 'Terminus facultés V', 'Aghroud terminus', 7.0),
('L31', 'SODISMA - IMIMIKI', 'Sodisma V', 'Imimiki Terminus', 6.0),
('L32', 'MOUQUAOUAMA SUD INBIAT - TAGHAZOUT', 'Mouquaouama Sud Inbiaat V', 'Taghazout Village', 5.0),
('L33', 'MOUQUAOUAMA SUD INBIAT - TAMRI', 'Mouquaouama Sud Inbiaat V', 'Tamri Centre', 4.0),
('L35', 'PLACE INEZGANE - TEMSIA', 'Place Inezgane', 'Temsia 9-Terminus', 3.0),
('L36', 'PLACE INEZGANE - OULED TEIMA', 'Place Inezgane', 'Terminus Ouled Teima', 2.0),
('L37', 'JIHADIA SOUK INEZGANE - LAGFIFAT', 'Jihadia-Souk Inezgane', 'Aeroport', 13.0),
('L38', 'JIHADIA SOUK INEZGANE - TERMINUS TAMAIT', 'Jihadia-Souk Inezgane', 'Terminus Tamait', 10.0),
('L39', 'SIDI BIBI - TAKKAD', 'Sidi Bibi Centre', 'Terminus Takkad', 12.0),
('L40', 'PLACE INEZGANE - BIOUGRA', 'Place Inezgane', 'Terminus Biougra', 25.0),
('L41', 'PLACE INEZGANE - AIT AMIRA - BIOUGRA', 'Place Inezgane', 'Terminus Biougra', 11.0),
('L42', 'PLACE INEZGANE - AGHBALOU MASSA', 'Place Inezgane', 'Terminus Aghbalou', 15.0),
('L43', 'BIOUGRA - AIT BAHA', 'Terminus Biougra', 'Kasbah ait baha', 12.0),
('L72', 'WIFAQ - HOPITAL INTER AGADIR', 'Fac De Lettres', 'Clinique international AGA V', 14.0),
('L73', 'FAC DES LETTRES - CITÉE DES METIERS', 'Fac De Lettres', 'Cité des Métiers', 15.0),
('L95', 'EXPRESS P.E VALLEE DES OISEAUX - AIT MELLOUL', 'P.E. Vallée des oiseaux', 'Ait Melloul', 14.0),
('L97', 'JIHADIA SOUK INEZGANE - P.E VALLEE DES OISEAUX', 'Jihadia-Souk Inezgane V', 'P.E. Vallée des oiseaux V', 9.0),
('L98', 'PLACE INEZGANE - PORT', 'Place Inezgane V', 'Port de Commerce V', 12.0),
('L99', 'PLACE INEZGANE - P.E VALLEE DES OISEAUX', 'Place Inezgane V', 'P.E. Vallée des oiseaux V', 11.0);
""")

# Inserting data into the 'stop' table
cur.execute("""
INSERT INTO stop (stop_name, latitude, longitude, zone) VALUES
('Mouquaouama Sud Inbiat', 30.4250, -9.5980, 'AGADIR'),
('Hopital Hassan II', 30.4265, -9.5965, 'AGADIR'),
('P.E. Vallée des oiseaux', 30.4270, -9.5970, 'AGADIR'),
('Ait El Mouden Terminus', 30.4280, -9.5985, 'AGADIR'),
('Houda Terminus', 30.4290, -9.5990, 'AGADIR'),
('Drarga Iguerer', 30.4300, -9.6000, 'AGADIR'),
('Fac De Lettres', 30.4310, -9.6010, 'AGADIR'),
('Masdoura', 30.4320, -9.6020, 'AGADIR'),
('Sodisma V', 30.4330, -9.6030, 'AGADIR'),
('Taddart 3', 30.4340, -9.6040, 'AGADIR'),
('Jihadia-Souk Inezgane', 30.4350, -9.6050, 'AGADIR'),
('Piscine Bourj', 30.4360, -9.6060, 'AGADIR'),
('Poste Inezgane Mesdoura', 30.4370, -9.6070, 'AGADIR'),
('Marina V', 30.4380, -9.6080, 'AGADIR'),
('Argana Souk', 30.4390, -9.6090, 'AGADIR'),
('Kasbah Tahar', 30.4400, -9.6100, 'AGADIR'),
('Tilila-L''Khawarizmi V', 30.4410, -9.6110, 'AGADIR'),
('Adrar Terminus', 30.4420, -9.6120, 'AGADIR'),
('Complexe Commercial Ain', 30.4430, -9.6130, 'AGADIR'),
('Winxo kolea V', 30.4440, -9.6140, 'AGADIR'),
('El Hajeb Marche Municipal', 30.4450, -9.6150, 'AGADIR'),
('Lamzar Mosquee', 30.4460, -9.6160, 'AGADIR'),
('Agadir Kasbah Oufela', 30.4470, -9.6170, 'AGADIR'),
('Temsia 9-Terminus', 30.4480, -9.6180, 'AGADIR'),
('Terminus Ouled Teima', 30.4490, -9.6190, 'AGADIR'),
('Aeroport', 30.4500, -9.6200, 'AGADIR'),
('Terminus Tamait', 30.4510, -9.6210, 'AGADIR'),
('Sidi Bibi Centre', 30.4520, -9.6220, 'AGADIR'),
('Terminus Takkad', 30.4530, -9.6230, 'AGADIR'),
('Terminus Biougra', 30.4540, -9.6240, 'AGADIR'),
('Kasbah ait baha', 30.4550, -9.6250, 'AGADIR'),
('Clinique international AGA V', 30.4560, -9.6260, 'AGADIR'),
('Cité des Métiers', 30.4570, -9.6270, 'AGADIR'),
('Port de Commerce V', 30.4580, -9.6280, 'AGADIR'),
('P.E. Vallée des oiseaux V', 30.4590, -9.6290, 'AGADIR'),
('Ait Melloul V', 30.4600, -9.6300, 'AGADIR'),
('Taghazout Village', 30.4610, -9.6310, 'AGADIR'),
('Tamri Centre', 30.4620, -9.6320, 'AGADIR'),
('Temsia', 30.4630, -9.6330, 'AGADIR'),
('Ouled Teima', 30.4640, -9.6340, 'AGADIR'),
('Lagfifat', 30.4650, -9.6350, 'AGADIR'),
('Terminus Takkad V', 30.4660, -9.6360, 'AGADIR'),
('Terminus Aghbalou V', 30.4670, -9.6370, 'AGADIR');
""")

# Inserting data into the 'trip' table
# This is a complex query that needs to reference the primary keys of 'bus' and 'bus_line'.
# It is best to handle this programmatically to avoid hardcoding IDs.
# However, based on your structure, I've manually mapped the IDs assuming an ordered insertion.
cur.execute("""
INSERT INTO trip (id_bus, id_line, driver_name, start_datetime, end_datetime, passenger_count, status, stop_time) VALUES
(1, 1, 'Mohamed El Fassi', '2025-08-05 07:00:00', '2025-08-05 07:45:00', 8, 'Terminé', '07:10:00'),
(2, 2, 'Khalid Amrani', '2025-08-05 07:30:00', '2025-08-05 08:10:00', 10, 'Terminé', '07:20:00'),
(3, 3, 'Fatima Zahra oulhaj', '2025-08-05 08:00:00', '2025-08-05 08:40:00', 6, 'Terminé', '07:30:00'),
(4, 4, 'Ahmed El Youssfi', '2025-08-05 08:15:00', '2025-08-05 09:00:00', 9, 'Terminé', '07:40:00'),
(5, 5, 'Samira El Amrani', '2025-08-05 08:30:00', '2025-08-05 09:15:00', 11, 'Terminé', '07:50:00'),
(6, 6, 'Youssef El Idrissi', '2025-08-05 08:45:00', '2025-08-05 09:30:00', 4, 'Terminé', '08:00:00'),
(7, 7, 'Nadia El Ouardi', '2025-08-05 09:00:00', '2025-08-05 10:00:00', 7, 'Terminé', '08:10:00'),
(8, 8, 'Hassan El Khatib', '2025-08-05 09:15:00', '2025-08-05 10:15:00', 5, 'Terminé', '08:20:00'),
(9, 9, 'Zineb El Housni', '2025-08-05 09:30:00', '2025-08-05 10:30:00', 6, 'Terminé', '08:30:00'),
(10, 10, 'Omar El Ghali', '2025-08-05 09:45:00', '2025-08-05 10:30:00', 4, 'Terminé', '08:40:00'),
(11, 11, 'Sofia El Amrani', '2025-08-05 10:00:00', '2025-08-05 10:45:00', 5, 'Terminé', '08:50:00'),
(12, 12, 'Khalid Amrani', '2025-08-05 10:30:00', '2025-08-05 11:00:00', 6, 'Terminé', '09:00:00'),
(13, 13, 'Mohamed El Fassi', '2025-08-05 10:15:00', '2025-08-05 10:45:00', 3, 'Terminé', '09:00:00'),
(14, 14, 'Fatima Zahra', '2025-08-05 10:45:00', '2025-08-05 11:15:00', 9, 'Terminé', '09:00:00'),
(15, 15, 'Ahmed El Youssfi', '2025-08-05 11:00:00', '2025-08-05 11:45:00', 5, 'Terminé', '09:00:00'),
(16, 16, 'Samira El Amrani', '2025-08-05 11:15:00', '2025-08-05 12:00:00', 4, 'Terminé', '09:00:00'),
(17, 17, 'Youssef El Idrissi', '2025-08-05 11:30:00', '2025-08-05 12:15:00', 8, 'Terminé', '09:00:00'),
(18, 18, 'Rachid El Fassi', '2025-08-05 11:45:00', '2025-08-05 12:30:00', 7, 'Terminé', '09:00:00'),
(19, 19, 'Nadia El Ouardi', '2025-08-05 12:00:00', '2025-08-05 12:45:00', 6, 'Terminé', '09:00:00'),
(20, 20, 'Hassan El Khatib', '2025-08-05 12:15:00', '2025-08-05 13:00:00', 10, 'Terminé', '09:00:00'),
(21, 21, 'Zineb El Housni', '2025-08-05 12:30:00', '2025-08-05 13:15:00', 5, 'Terminé', '09:00:00'),
(22, 22, 'Omar El Ghali', '2025-08-05 12:45:00', '2025-08-05 13:30:00', 4, 'Terminé', '09:00:00'),
(23, 23, 'Sofia El Amrani', '2025-08-05 13:00:00', '2025-08-05 13:45:00', 3, 'Terminé', '09:00:00'),
(24, 24, 'Mohamed El Fassi', '2025-08-05 13:15:00', '2025-08-05 14:00:00', 2, 'Terminé', '09:00:00'),
(25, 25, 'Khalid Amrani', '2025-08-05 13:30:00', '2025-08-05 14:15:00', 1, 'Terminé', '09:00:00'),
(26, 26, 'Fatima Zahra', '2025-08-05 13:45:00', '2025-08-05 14:30:00', 7, 'Terminé', '09:00:00'),
(27, 27, 'Ahmed El Youssfi', '2025-08-05 14:00:00', '2025-08-05 14:45:00', 8, 'Terminé', '09:00:00'),
(28, 28, 'Samira El Amrani', '2025-08-05 14:15:00', '2025-08-05 15:00:00', 5, 'Terminé', '09:00:00'),
(29, 29, 'Youssef El Idrissi', '2025-08-05 14:30:00', '2025-08-05 15:15:00', 8, 'Terminé', '09:00:00'),
(30, 30, 'Rachid El Fassi', '2025-08-05 14:45:00', '2025-08-05 15:30:00', 2, 'Terminé', '09:00:00'),
(31, 31, 'Nadia El Ouardi', '2025-08-05 15:00:00', '2025-08-05 15:45:00', 1, 'Terminé', '09:00:00'),
(32, 32, 'Hassan El Khatib', '2025-08-05 15:15:00', '2025-08-05 16:00:00', 4, 'Terminé', '09:00:00'),
(33, 33, 'Zineb El Housni', '2025-08-05 15:30:00', '2025-08-05 16:15:00', 9, 'Terminé', '09:00:00'),
(34, 34, 'Omar El Ghali', '2025-08-05 15:45:00', '2025-08-05 16:30:00', 2, 'Terminé', '09:00:00'),
(35, 35, 'Sofia El Amrani', '2025-08-05 16:00:00', '2025-08-05 16:45:00', 3, 'Terminé', '09:00:00'),
(36, 36, 'Mohamed El Fassi', '2025-08-05 16:15:00', '2025-08-05 17:00:00', 8, 'Terminé', '09:00:00'),
(37, 37, 'Khalid Amrani', '2025-08-05 16:30:00', '2025-08-05 17:15:00', 7, 'Terminé', '09:00:00'),
(38, 38, 'Fatima Zahra', '2025-08-05 16:45:00', '2025-08-05 17:30:00', 10, 'Terminé', '09:00:00'),
(39, 39, 'Ahmed El Youssfi', '2025-08-05 17:00:00', '2025-08-05 17:45:00', 1, 'Terminé', '09:00:00');
""")

# Commit changes to the database
conn.commit()
print("Base de données et tables créées et remplies avec succès.")

# Close the cursor and connection
cur.close()
conn.close()

