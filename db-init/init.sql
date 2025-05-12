CREATE TABLE if NOT EXISTS beehives (
    beehive_id SERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE,
    location POINT,
    installation_date DATE,
    last_inspection_date DATE,
    notes TEXT
);

CREATE TABLE if NOT EXISTS weather_stations (
    weather_id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    location POINT,
    installation_date DATE,
    notes TEXT
);

CREATE TABLE if NOT EXISTS sensors (
    sensor_id SERIAL PRIMARY KEY,
    sensor_name VARCHAR(50) UNIQUE,
    sensor_type VARCHAR(50),
    measurement_units TEXT,
    installation_date DATE,
    last_seen TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE if NOT EXISTS data (
    reading_id SERIAL PRIMARY KEY,
    sensor_id INT REFERENCES sensors(sensor_id),
    measurement_unit VARCHAR(50),
    ts TIMESTAMP,
    value FLOAT NOT NULL
);

CREATE TABLE if NOT EXISTS sensor_mapping (
    mapping_id SERIAL PRIMARY KEY,
    sensor_id INT REFERENCES sensors(sensor_id),
    beehive_id INT REFERENCES beehives(beehive_id),
    weather_id INT REFERENCES weather_stations(weather_id),
    UNIQUE(sensor_id, beehive_id, weather_id)
);

-- initialise 42 beehives
INSERT INTO beehives (name, location, installation_date, last_inspection_date, notes) VALUES
('Larry',  POINT(49.15182633037482, 9.215298005933729), '2025-04-14', '2025-04-14', 'Larry is standing alone, he needs some friends'),
('TamTam', POINT(49.15184249515977, 9.21529330883642),  '2025-04-14', '2025-04-14', 'TamTam is the middle Sandwhich child'),
('BonBon', POINT(49.151846188225065, 9.215281522540364), '2025-04-14', '2025-04-14', 'BonBon is the smallest yet most active')
ON CONFLICT (name) DO NOTHING;

