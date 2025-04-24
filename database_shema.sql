CREATE TABLE beehives (
    beehive_id SERIAL PRIMARY KEY,
    name VARCHAR(20),
    location POINT,
    installation_date DATE,
    last_inspection_date DATE,
    notes TEXT
);

CREATE TABLE sensors (
    sensor_id SERIAL PRIMARY KEY,
    beehive_id SERIAL REFERENCES beehives(beehive_id),
    sensor_name VARCHAR(50),
    sensor_type VARCHAR(50),
    measurement_units TEXT[],
    installation_date TIMESTAMP,
    last_seen TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE data (
    reading_id SERIAL PRIMARY KEY,
    sensor_id SERIAL REFERENCES sensors(sensor_id),
    beehive_id SERIAL REFERENCES beehives(beehive_id),
    measurement_unit VARCHAR(50)
    timestamp TIMESTAMP,
    value FLOAT NOT NULL, 
);

