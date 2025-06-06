CREATE TABLE if NOT EXISTS beehives (
    beehive_id SERIAL PRIMARY KEY,
    name VARCHAR(20),
    location POINT,
    installation_date DATE,
    last_inspection_date DATE,
    notes TEXT
);

CREATE TABLE if NOT EXISTS sensors (
    sensor_id SERIAL PRIMARY KEY,
    sensor_name VARCHAR(50),
    sensor_type VARCHAR(50),
    installation_date DATE,
    last_seen TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE if NOT EXISTS data (
    reading_id SERIAL PRIMARY KEY,
    sensor_id INTEGER REFERENCES sensors(sensor_id),
    beehive_id INTEGER REFERENCES beehives(beehive_id),
    unit_id INTEGER REFERENCES measurement_units(unit_id),
    ts TIMESTAMP,
    value FLOAT NOT NULL
);

CREATE TABLE if NOT EXISTS measurement_units (
    unit_id SERAIL PRIMARY KEY,
    sensord_id SERAIL REFERENCES sensors(sensord_id),
    unit_name VARCHAR(50) UNIQUE NOT NULL,
);

CREATE TABLE if NOT EXISTS beehive_sensors (
    beehive_id INTEGER REFERENCES beehives(beehive_id),
    sensor_id INTEGER REFERENCES sensors(sensor_id),
    PRIMARY KEY (beehive_id, sensor_id)
);