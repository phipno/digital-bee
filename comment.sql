BEGIN;

-- 1. First identify all current sensor IDs for reference
CREATE TEMPORARY TABLE current_sensors AS
SELECT sensor_id, sensor_name, beehive_id FROM sensors
WHERE sensor_name IN (
    'LoRa-2CF7F1C0613005BC',
    'LoRa-A840411F645AE815',
    'LoRa-A8404138A188669C',
    'LoRa-A84041892E5A7A68',
    'LoRa-A840419521864618',
    'LoRa-A84041CC625AE81E'
);

-- 2. Update all sensor assignments according to new mapping
-- Move LoRa-A84041892E5A7A68 from beehive 2 to 1
UPDATE sensors SET beehive_id = 1 
WHERE sensor_name = 'LoRa-A84041892E5A7A68';

-- Move LoRa-A84041CC625AE81E from beehive 3 to 2
UPDATE sensors SET beehive_id = 2 
WHERE sensor_name = 'LoRa-A84041CC625AE81E';

-- Move LoRa-A840419521864618 from beehive 3 to 2
UPDATE sensors SET beehive_id = 2 
WHERE sensor_name = 'LoRa-A840419521864618';

-- Move LoRa-A8404138A188669C from beehive 2 to 3
UPDATE sensors SET beehive_id = 3 
WHERE sensor_name = 'LoRa-A8404138A188669C';

-- 4. Update beehive_id in data table for all moved sensors
UPDATE data d
SET beehive_id = s.beehive_id
FROM sensors s
WHERE d.sensor_id = s.sensor_id
AND s.sensor_name IN (
    'LoRa-A84041892E5A7A68',
    'LoRa-A84041CC625AE81E',
    'LoRa-A840419521864618',
    'LoRa-A8404138A188669C'
);

-- 5. Verify all changes
SELECT s.sensor_id, s.sensor_name, s.beehive_id, 
       COUNT(d.reading_id) as reading_count
FROM sensors s
LEFT JOIN data d ON s.sensor_id = d.sensor_id
WHERE s.sensor_name IN (
    'LoRa-2CF7F1C0613005BC',
    'LoRa-A840411F645AE815',
    'LoRa-A8404138A188669C',
    'LoRa-A84041892E5A7A68',
    'LoRa-A840419521864618',
    'LoRa-A84041CC625AE81E',
    'LoRa-A8494160C85A7A7B'
)
GROUP BY s.sensor_id, s.sensor_name, s.beehive_id
ORDER BY s.beehive_id, s.sensor_name;

COMMIT;