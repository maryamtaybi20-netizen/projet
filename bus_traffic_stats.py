import psycopg2
from datetime import datetime 

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

    
cur.execute("""
    INSERT INTO bus (bus_number, capacity) VALUES
    ('BUS001', 100),
    ('BUS002', 100),
    ('BUS003', 100),
    ('BUS004', 100),
    ('BUS005', 100),
    ('BUS006', 100),
    ('BUS007', 100),
    ('BUS008', 100),
    ('BUS009', 100),
    ('BUS010', 100),
    ('BUS011', 100),
    ('BUS012', 100),
    ('BUS013', 100),
    ('BUS014', 100),
    ('BUS015', 100),
    ('BUS016', 100),
    ('BUS017', 100),
    ('BUS018', 100),
    ('BUS019', 100),
    ('BUS020', 100),
    ('BUS021', 100),
    ('BUS022', 100),
    ('BUS023', 100),
    ('BUS024', 100),
    ('BUS025', 100),
    ('BUS026', 100),
    ('BUS027', 100),
    ('BUS028', 100),
    ('BUS029', 100),
    ('BUS030', 100),
    ('BUS031', 100),
    ('BUS032', 100),
    ('BUS033', 100),
    ('BUS034', 100),
    ('BUS035', 100),
    ('BUS036', 100),
    ('BUS037', 100),
    ('BUS038', 100),
    ('BUS039', 100),
    ('BUS040', 100);
    """)

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
    ('L37', 'JIHADIA SOUK INEZGANE - LAGFIFAT', 'Jihadia-Souk Inezgane', 'Aeroport', 1.5),
    ('L38', 'JIHADIA SOUK INEZGANE - TERMINUS TAMAIT', 'Jihadia-Souk Inezgane', 'Terminus Tamait', 1.5),
    ('L39', 'SIDI BIBI - TAKKAD', 'Sidi Bibi Centre', 'Terminus Takkad', 1.5),
    ('L40', 'PLACE INEZGANE - BIOUGRA', 'Place Inezgane', 'Terminus Biougra', 25.0),
    ('L41', 'PLACE INEZGANE - AIT AMIRA - BIOUGRA', 'Place Inezgane', 'Terminus Biougra', 1.5),
    ('L42', 'PLACE INEZGANE - AGHBALOU MASSA', 'Place Inezgane', 'Terminus Aghbalou', 1.5),
    ('L43', 'BIOUGRA - AIT BAHA', 'Terminus Biougra', 'Kasbah ait baha', 1.5),
    ('L72', 'WIFAQ - HOPITAL INTER AGADIR', 'Fac De Lettres', 'Clinique international AGA V', 1.5),
    ('L73', 'FAC DES LETTRES - CITÉE DES METIERS', 'Fac De Lettres', 'Cité des Métiers', 15.0),
    ('L95', 'EXPRESS P.E VALLEE DES OISEAUX - AIT MELLOUL', 'P.E. Vallée des oiseaux', 'Ait Melloul', 1.5),
    ('L97', 'JIHADIA SOUK INEZGANE - P.E VALLEE DES OISEAUX', 'Jihadia-Souk Inezgane V', 'P.E. Vallée des oiseaux V', 1.5),
    ('L98', 'PLACE INEZGANE - PORT', 'Place Inezgane V', 'Port de Commerce V', 12.0),
    ('L99', 'PLACE INEZGANE - P.E VALLEE DES OISEAUX', 'Place Inezgane V', 'P.E. Vallée des oiseaux V', 11.0);
    """)

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
 
cur.execute("""
    INSERT INTO trip (id_bus, line_number, line_name, origin, destination, distance_km, start_datetime, end_datetime, driver_name, status) VALUES
    (1, 'L1', 'MOUQUAOUAMA SUD INBIAT - HOPITAL HASSAN II', 'Mouquaouama Sud Inbiaat', 'Terminus hôpital Hassan II V', 12.5, '2025-08-05 07:00:00', '2025-08-05 07:45:00', 'Mohamed El Fassi', 'Terminé'),
    (2, 'L2', 'P.E VALLEE DES OISEAUX - HAY MOHAMMEDI', 'P.E. Vallée des oiseaux', 'Ait El Mouden Terminus', 10.0, '2025-08-05 07:30:00', '2025-08-05 08:10:00', 'Khalid Amrani', 'Terminé'),
    (3, 'L3', 'P.E VALLEE DES OISEAUX - ELHOUDA', 'P.E. Vallée des oiseaux', 'Houda Terminus', 8.5, '2025-08-05 08:00:00', '2025-08-05 08:40:00', 'Fatima Zahra oulhaj', 'Terminé'),
    (4, 'L5', 'P.E VALLEE DES OISEAUX - DRARGA', 'P.E. Vallée des oiseaux', 'Drarga Iguerer', 15.0, '2025-08-05 08:15:00', '2025-08-05 09:00:00', 'Ahmed El Youssfi', 'Terminé'),
    (5, 'L6', 'FACULTE - MESDOURA', 'Fac De Lettres', 'Terminus Masdoura', 9.0, '2025-08-05 08:30:00', '2025-08-05 09:15:00', 'Samira El Amrani', 'Terminé'),
    (6, 'L8', 'SODISMA - TADDART', 'Sodisma V', 'Taddart 3', 7.0, '2025-08-05 08:45:00', '2025-08-05 09:30:00', 'Youssef El Idrissi', 'Terminé'),
    (7, 'L9', 'JIHADIA SOUK INEZGANE - DRARGA', 'Jihadia-Souk Inezgane', 'Drarga Iguerer', 14.0, '2025-08-05 09:00:00', '2025-08-05 10:00:00', 'Nadia El Ouardi', 'Terminé'),
    (8, 'L10', 'INEZGANE - LAKHCHICHAT', 'Jihadia-Souk Inezgane V', 'Piscine Bourj', 8.0, '2025-08-05 09:15:00', '2025-08-05 10:15:00', 'Hassan El Khatib', 'Terminé'),
    (9, 'L11', 'P.E VALLEE DES OISEAUX - POSTE INEZGANE MESDOURA', 'P.E. Vallée des oiseaux', 'Poste Inezgane Mesdoura', 11.0, '2025-08-05 09:30:00', '2025-08-05 10:30:00', 'Zineb El Housni', 'Terminé'),
    (10, 'L12', 'MARINA - AIT MELLOUL', 'MARINA V', 'Marbre Amenou', 5.0, '2025-08-05 09:45:00', '2025-08-05 10:30:00', 'Omar El Ghali', 'Terminé'),
    (11, 'L13', 'JIHADIA SOUK INEZGANE - ARGANA', 'Jihadia-Souk Inezgane', 'Argana Souk', 6.5, '2025-08-05 10:00:00', '2025-08-05 10:45:00', 'Sofia El Amrani', 'Terminé'),
    (12, 'L14', 'JIHADIA SOUK INEZGANE - KASBAH TAHAR', 'Jihadia-Souk Inezgane', 'Kasbah 1 V', 4.5, '2025-08-05 10:15:00', '2025-08-05 10:45:00', 'Mohamed El Fassi', 'Terminé'),
    (13, 'L15', 'TILILA - POSTE INZEGANE', 'Jihadia-Souk Inezgane V', 'Tilila-L''Khawarizmi V', 3.5, '2025-08-05 10:30:00', '2025-08-05 11:00:00', 'Khalid Amrani', 'Terminé'),
    (14, 'L16', 'P.E VALLEE DES OISEAUX - ADRAR', 'P.E. Vallée des oiseaux', 'Adrar Terminus', 11.0, '2025-08-05 10:45:00', '2025-08-05 11:15:00', 'Fatima Zahra', 'Terminé'),
    (15, 'L20', 'PLACE INEZGANE - SOUK PRINCIPAL KOLEA', 'Place Inezgane', 'Complexe Commercial Ain', 9.0, '2025-08-05 11:00:00', '2025-08-05 11:45:00', 'Ahmed El Youssfi', 'Terminé'),
    (16, 'L21', 'PLACE INEZGANE - KOLEA', 'Bachaouia', 'Winxo kolea V', 5.0, '2025-08-05 11:15:00', '2025-08-05 12:00:00', 'Samira El Amrani', 'Terminé'),
    (17, 'L22', 'P.E VALLEE DES OISEAUX - EL HAJEB TIKIOUINE', 'P.E. Vallée des oiseaux', 'El Hajeb Marche Municipal', 10.0, '2025-08-05 11:30:00', '2025-08-05 12:15:00', 'Youssef El Idrissi', 'Terminé'),
    (18, 'L23', 'PLACE INZGANE - LAMZAR', 'Place Inezgane', 'Lamzar Mosquee', 6.0, '2025-08-05 11:45:00', '2025-08-05 12:30:00', 'Rachid El Fassi', 'Terminé'),
    (19, 'L24', 'KASBAH AGADIR OUFELLA', 'Pied Oufela Agadir', 'Agadir Kasbah Oufela', 8.0, '2025-08-05 12:00:00', '2025-08-05 12:45:00', 'Nadia El Ouardi', 'Terminé'),
    (20, 'L26', 'P.E VALLEE DES OISEAUX - WIFAQ - PLACE INEZGANE', 'P.E. Vallée des oiseaux', 'Place Inezgane V', 12.0, '2025-08-05 12:15:00', '2025-08-05 13:00:00', 'Hassan El Khatib', 'Terminé'),
    (21, 'L27', 'BARREAU - TERMINUS AGHROUD', 'Terminus facultés V', 'Aghroud terminus', 7.0, '2025-08-05 12:30:00', '2025-08-05 13:15:00', 'Zineb El Housni', 'Terminé'),
    (22, 'L31', 'SODISMA - IMIMIKI', 'Sodisma V', 'Imimiki Terminus', 6.0, '2025-08-05 12:45:00', '2025-08-05 13:30:00', 'Omar El Ghali', 'Terminé'),
    (23, 'L32', 'MOUQUAOUAMA SUD INBIAT - TAGHAZOUT', 'Mouquaouama Sud Inbiaat V', 'Taghazout Village', 5.0, '2025-08-05 13:00:00', '2025-08-05 13:45:00', 'Sofia El Amrani', 'Terminé'),
    (24, 'L33', 'MOUQUAOUAMA SUD INBIAT - TAMRI', 'Mouquaouama Sud Inbiaat V', 'Tamri Centre', 4.0, '2025-08-05 13:15:00', '2025-08-05 14:00:00', 'Mohamed El Fassi', 'Terminé'),
    (25, 'L35', 'PLACE INEZGANE - TEMSIA', 'Place Inezgane', 'Temsia 9-Terminus', 3.0, '2025-08-05 13:30:00', '2025-08-05 14:15:00', 'Khalid Amrani', 'Terminé'),
    (26, 'L36', 'PLACE INEZGANE - OULED TEIMA', 'Place Inezgane', 'Terminus Ouled Teima', 2.0, '2025-08-05 13:45:00', '2025-08-05 14:30:00', 'Fatima Zahra', 'Terminé'),
    (27, 'L37', 'JIHADIA SOUK INEZGANE - LAGFIFAT', 'Jihadia-Souk Inezgane', 'Aeroport', 13.0, '2025-08-05 14:00:00', '2025-08-05 14:45:00', 'Ahmed El Youssfi', 'Terminé'),
    (28, 'L38', 'JIHADIA SOUK INEZGANE - TERMINUS TAMAIT', 'Jihadia-Souk Inezgane', 'Terminus Tamait', 10.0, '2025-08-05 14:15:00', '2025-08-05 15:00:00', 'Samira El Amrani', 'Terminé'),
    (29, 'L39', 'SIDI BIBI - TAKKAD', 'Sidi Bibi Centre', 'Terminus Takkad', 12.0, '2025-08-05 14:30:00', '2025-08-05 15:15:00', 'Youssef El Idrissi', 'Terminé'),
    (30, 'L40', 'PLACE INEZGANE - BIOUGRA', 'Place Inezgane', 'Terminus Biougra', 25.0, '2025-08-05 14:45:00', '2025-08-05 15:30:00', 'Rachid El Fassi', 'Terminé'),
    (31, 'L41', 'PLACE INEZGANE - AIT AMIRA - BIOUGRA', 'Place Inezgane', 'Terminus Biougra', 11.0, '2025-08-05 15:00:00', '2025-08-05 15:45:00', 'Nadia El Ouardi', 'Terminé'),
    (32, 'L42', 'PLACE INEZGANE - AGHBALOU MASSA', 'Place Inezgane', 'Terminus Aghbalou', 15.0, '2025-08-05 15:15:00', '2025-08-05 16:00:00', 'Hassan El Khatib', 'Terminé'),
    (33, 'L43', 'BIOUGRA - AIT BAHA', 'Terminus Biougra', 'Kasbah ait baha', 12.0, '2025-08-05 15:30:00', '2025-08-05 16:15:00', 'Zineb El Housni', 'Terminé'),
    (34, 'L72', 'WIFAQ - HOPITAL INTER AGADIR', 'Fac De Lettres', 'Clinique international AGA V', 14, '2025-08-05 15:45:00', '2025-08-05 16:30:00', 'Omar El Ghali', 'Terminé'),
    (35, 'L73', 'FAC DES LETTRES - CITÉE DES METIERS', 'Fac De Lettres', 'Cité des Métiers', 15.0, '2025-08-05 16:00:00', '2025-08-05 16:45:00', 'Sofia El Amrani', 'Terminé'),
    (36, 'L95', 'EXPRESS P.E VALLEE DES OISEAUX - AIT MELLOUL', 'P.E. Vallée des oiseaux', 'Ait Melloul', 14, '2025-08-05 16:15:00', '2025-08-05 17:00:00', 'Mohamed El Fassi', 'Terminé'),
    (37, 'L97', 'JIHADIA SOUK INEZGANE - P.E VALLEE DES OISEAUX', 'Jihadia-Souk Inezgane V', 'P.E. Vallée des oiseaux V', 9.0, '2025-08-05 16:30:00', '2025-08-05 17:15:00', 'Khalid Amrani', 'Terminé'),
    (38, 'L98', 'PLACE INEZGANE - PORT', 'Place Inezgane V', 'Port de Commerce V', 12.0, '2025-08-05 16:45:00', '2025-08-05 17:30:00', 'Fatima Zahra', 'Terminé'),
    (39, 'L99', 'PLACE INEZGANE - P.E VALLEE DES OISEAUX', 'Place Inezgane V', 'P.E. Vallée des oiseaux V', 11.0, '2025-08-05 17:00:00', '2025-08-05 17:45:00', 'Ahmed El Youssfi', 'Terminé');
    """)

     
cur.execute("""
    INSERT INTO trip_stop (id_trip, id_stop, stop_time, passenger_count) VALUES
    (1, 1, '07:00:00', 5),
    (1, 2, '07:10:00', 8),
    (1, 3, '07:20:00', 10),
    (1, 4, '07:30:00', 7),
    (2, 5, '07:30:00', 6),
    (2, 6, '07:40:00', 9),
    (2, 7, '07:50:00', 11),
    (3, 8, '08:00:00', 4),
    (3, 9, '08:10:00', 7),
    (3, 10, '08:20:00', 5),
    (4, 11, '08:30:00', 12),
    (4, 12, '08:40:00', 8),
    (4, 13, '08:50:00', 10),
    (5, 14, '09:00:00', 6),
    (5, 15, '09:10:00', 9),
    (5, 16, '09:20:00', 11),
    (6, 17, '09:30:00', 7),
    (6, 18, '09:40:00', 8),
    (6, 19, '09:50:00', 10),
    (7, 20, '10:00:00', 5),
    (7, 21, '10:10:00', 6),
    (7, 22, '10:20:00', 7),
    (8, 23, '10:30:00', 8),
    (8, 24, '10:40:00', 9),
    (8, 25, '10:50:00', 10),
    (9, 26, '11:00:00', 11),
    (9, 27, '11:10:00', 12),
    (9, 28, '11:20:00', 13),
    (10, 29, '11:30:00', 14),
    (10, 30, '11:40:00', 15),
    (10, 31, '11:50:00', 16),
    (11, 32, '12:00:00', 17),
    (11, 33, '12:10:00', 18),
    (11, 34, '12:20:00', 19),
    (11, 35, '12:30:00', 20),
    (11, 36, '12:40:00', 21),
    (11, 37, '12:50:00', 22),
    (11, 38, '13:00:00', 23),
    (11, 39, '13:10:00', 24),
    (11, 40, '13:20:00', 25),
    (11, 41, '13:30:00', 26),
    (11, 42, '13:40:00', 27),
    (11, 43, '13:50:00', 28),
    (12, 1, '14:00:00', 29),
    (12, 2, '14:10:00', 30),
    (12, 3, '14:20:00', 31),
    (12, 4, '14:30:00', 32),
    (12, 5, '14:40:00', 33),
    (12, 6, '14:50:00', 34),
    (12, 7, '15:00:00', 35),
    (12, 8, '15:10:00', 36),
    (12, 9, '15:20:00', 37),
    (12, 10, '15:30:00', 38),
    (13, 11, '15:40:00', 39),
    (13, 12, '15:50:00', 40),
    (13, 13, '16:00:00', 41),
    (13, 14, '16:10:00', 42),
    (13, 15, '16:20:00', 43),
    (13, 16, '16:30:00', 44),
    (13, 17, '16:40:00', 45),
    (13, 18, '16:50:00', 46),
    (13, 19, '17:00:00', 47),
    (13, 20, '17:10:00', 48);
    """)
conn.commit()
print("Base de données et tables créées avec succès.")


