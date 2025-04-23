CREATE TABLE beehives (
    beehive_id SERIAL PRIMARY KEY,
    name VARCHAR(20),
    location GEOMETRY(Point),
    installation_date DATE,
    last_inspection_date DATE,
    notes TEXT,
);

CREATE TABLE sensors (
    sensor_id SERIAL PRIMARY KEY,
    beehive_id SERIAL REFERENCES beehive_id(beehive_id),
    sensor_type VARCHAR(20),
    name VARCHAR(50),
    installation_date TIMESTAMP
);

CREATE TABLE data (
    reading_id SERIAL PRIMARY KEY,
    sensor_id SERIAL REFERENCES sensors(sensor_id),
    timestamp TIMESTAMP,
    value FLOAT,
    battery_level FLOAT,
);

CREATE INDEX idx_sensor_readings_timestamp ON sensor_readings(timestamp);
CREATE INDEX idx_sensor_readings_sensor_id ON sensor_readings(sensor_id);
