CREATE TABLE IF NOT EXISTS location (
	id SERIAL PRIMARY KEY,
	location_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS beehive (
	id SERIAL PRIMARY KEY,
	installation_date TIMESTAMP NOT NULL,
	location_id INTEGER NOT NULL,
	FOREIGN KEY (location_id) REFERENCES location(id)
);

CREATE TABLE IF NOT EXISTS sensor (
	id UUID PRIMARY KEY,
	device_type TEXT,
	device_name TEXT,
	last_activity TIMESTAMP NOT NULL DEFAULT now(),
	beehive_id INTEGER NOT NULL DEFAULT 1
	-- FOREIGN KEY (beehive_id) REFERENCES beehive(id)
);

CREATE TABLE IF NOT EXISTS measurement_type (
	id SERIAL PRIMARY KEY,
	name TEXT UNIQUE,
	unit TEXT
);

CREATE TABLE IF NOT EXISTS sensor_measurement (
	id SERIAL PRIMARY KEY,
	sensor_id UUID NOT NULL,
	measurement_type_id INTEGER NOT NULL,
	FOREIGN KEY (sensor_id) REFERENCES sensor(id),
	FOREIGN KEY (measurement_type_id) REFERENCES measurement_type(id)
);

CREATE TABLE IF NOT EXISTS data (
	id SERIAL PRIMARY KEY,
	value DOUBLE PRECISION NOT NULL,
	time TIMESTAMP NOT NULL,
	sensor_id UUID NOT NULL,
	measurement_type_id INTEGER NOT NULL,
	FOREIGN KEY (sensor_id) REFERENCES sensor(id),
	FOREIGN KEY (measurement_type_id) REFERENCES measurement_type(id)
);
