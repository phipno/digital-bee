CREATE TABLE beehive (
    hive_id INT PRIMARY KEY,
    name ,
    location ,
    installation_date DATE
    last_inspection_date DATE,
    notes TEXT,
    sensors [],
    reading [],
);

CREATE TABLE sensors (
    sensor_id INT PRIMARY KEY,
    sensor_type ,
    name ,
    installation_date DATE,
);

CREATE TABLE reading (
    timestamp DATE,
    temprature VALUE,
    weight VALUE,
    
)