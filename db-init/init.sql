CREATE TABLE if NOT EXISTS beehives (
    beehive_id SERIAL PRIMARY KEY,
    name VARCHAR(20),
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