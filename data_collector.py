# *--------------------------------------------------------------------------------------*#
# *                                                                                .|    *#
# *     $FILENAME                 data_collector.py    /     (__)          |/            *#
# *                                                          (oo)------/'   ,__,    ,    *#
# *     By: $AUTHOR                          phipno       |  (__)     ||    (oo)_____/   *#
# *                                                             ||---/||    (__)    ||   *#
# *     Created: $CREATEDAT 2025.04.18    by phipno   |/                  ,    ||--w||   *#
# *                                                  ,,       !              |'          *#
# *                                                       ,           ,|             |/  *#
# *----------------8<------------------[ mooooooo ]--------------------------------------*#

from dotenv import load_dotenv
import os
import requests
import json
import datetime
from datetime import datetime
import time
import psycopg2
from psycopg2 import sql

load_dotenv()

beehive_api_url = os.getenv('BEEHIVE_API_URL')
beehive_api_key = os.getenv('BEEHIVE_API_KEY')

wather_api_url = os.getenv('WEATHER_API_URL')
wather_api_url = os.getenv('WEATHER_API_KEY')

sensor_entities = []


db_name = os.getenv('DB_NAME')
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT')

conn = psycopg2.connect(database=db_name,
                        host='localhost',
                        user=db_user,
                        password=db_pass,
                        port=db_port)
cursor = conn.cursor()

def create_sensor_entry(beehive_id, name, type, units, installation_date, last_seen, is_active):
    insert_query = """
    INSERT INTO sensors (beehive_id, sensor_name, sensor_type, measurement_units, installation_date, last_seen, is_active)
    VALUES (%s, %s, %s, %s, TO_DATE(%s, %s), to_timestamp(%s), %s)
    RETURNING *
    """

    cursor.execute(insert_query, (
        beehive_id,
        name,
        type,
        units,
        installation_date[0],
        installation_date[1],
        last_seen,
        is_active
    ))
    new_row = cursor.fetchone()
    conn.commit()
    return new_row

def create_beehive_entry(name, location, installation_date, last_inspection_date, notes):
    insert_query = """
    INSERT INTO beehives (name, location, installation_date, last_inspection_date, notes)
    VALUES (%s, %s, TO_DATE(%s, %s), TO_DATE(%s, %s), %s)
    """

    cursor.execute(insert_query, (
        name,
        location,
        installation_date[0],
        installation_date[1],
        last_inspection_date[0],
        last_inspection_date[1],
        notes
    ))
    conn.commit()

# create_beehive_entry(
#     "Larry",
#     "(49.15182633037482, 9.215298005933729)",
#     ['2025-04-14', 'YYYY-MM-DD'],
#     ['2025-04-14', 'YYYY-MM-DD'],
#     "Larry is standing alone, he needs some friends i guess"
# )
# create_beehive_entry(
#     "TamTam",
#     "(49.15184249515977, 9.21529330883642)",
#     ['2025-04-14', 'YYYY-MM-DD'],
#     ['2025-04-14', 'YYYY-MM-DD'],
#     "TamTam is the middle Sandwhich child"
# )
# create_beehive_entry(
#     "BonBon",
#     "(49.151846188225065, 9.215281522540364)",
#     ['2025-04-14', 'YYYY-MM-DD'],
#     ['2025-04-14', 'YYYY-MM-DD'],
#     "BonBon is the smallest of them all yet the most active"
# )

def create_data_table(table_name):
    query = sql.SQL("""
    CREATE TABLE {} (
            reading_id SERIAL PRIMARY KEY,
            sensor_id SERIAL REFERENCES sensors(sensor_id),
            beehive_id SERIAL REFERENCES beehives(beehive_id),
            measurement_unit VARCHAR(50),
            ts TIMESTAMP,
            value FLOAT NOT NULL
        )
    """).format(sql.Identifier(table_name))

    cursor.execute(query)

    conn.commit()
    return

def insert_values_data(sensor_id, beehive_id, table_name, unit, ts, value):
    query = sql.SQL("""
    INSERT INTO {} (sensor_id, beehive_id, measurement_unit, ts, value)
    VALUES (%s, %s, %s, to_timestamp(%s), %s)
    """).format(sql.Identifier(table_name))

    cursor.execute(query, (
        sensor_id,
        beehive_id,
        unit, 
        ts,
        value
    ))
    conn.commit()
    return

# leave as comment only for reference
# CREATE TABLE sensor_name_unit (
#     reading_id SERIAL PRIMARY KEY,
#     sensor_id SERIAL REFERENCES sensors(sensor_id),
#     beehive_id SERIAL REFERENCES beehives(beehive_id),
#     measurement_unit VARCHAR(50),
#     ts TIMESTAMP,
#     value FLOAT NOT NULL
# ); 

def fetch_beehive_api_paths():
    """Fetch data from the digital beehive API"""
    try:
        response = requests.get(beehive_api_url + "?x-apikey=" + beehive_api_key)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error", e)
        return None

def parse_api_paths(response):
    return [group['authGroupName'] for group in response['authGroup']]

def fetch_sensor_groups_data():
    """Fetch data from each group"""
    responses = []
    for sensor in sensor_entities:
        try:
            response = requests.get(beehive_api_url + "/" + sensor + "/entityId" + "?page=0" + "&x-apikey=" + beehive_api_key)
            response.raise_for_status()
            responses.append(response.json())
        except requests.exceptions.RequestException as e:
            print("Error for sensor", sensor , e)
            # TODO needs error handling or retrying and notifcation
    return responses
    
def get_row_by_varchar(table_name, column_name, value_to_check):
    query = sql.SQL("SELECT * FROM {} WHERE {} = %s").format(
        sql.Identifier(table_name), 
        sql.Identifier(column_name)
    )
    cursor.execute(query, (value_to_check,))
    return cursor.fetchone()

def get_table(table_name, shema="public"):
    """CHeck if a table exists using pg_catalog"""
    query = """
        SELECT EXISTS(
            SELECT 1
            FROM pg_catalog.pg_tables
            WHERE schemaname = %s
            AND tablename = %s
        );
    """
    cursor.execute(query, (shema, table_name))
    return cursor.fetchone()[0]

sensor_in_beehive = [{
    "sensor_name": "LoRa-2CF7F1C0613005BC",
    "beehive_id": 1,
}, {
    "sensor_name": "LoRa-A840411F645AE815",
    "beehive_id": 1,
},
{
    "sensor_name": "LoRa-A8404138A188669C",
    "beehive_id": 2,
},
{
    "sensor_name": "LoRa-A84041892E5A7A68",
    "beehive_id": 2,
},
{
    "sensor_name": "LoRa-A840419521864618",
    "beehive_id": 3,
},
{
    "sensor_name": "LoRa-A84041CC625AE81E",
    "beehive_id": 3,
}]

def get_beehive_for_sensor(sensor_name):
    for data in sensor_in_beehive:
        if data["sensor_name"] == sensor_name:
            print("BEEHIVE IS: ", data["beehive_id"])
            return data["beehive_id"];
    return 0

def format_for_postgres(data):
    """For later parsing to postgres"""
    for data_group, sensor_group in zip(data, sensor_entities):
        print(sensor_group, " ", sensor_group, " ", sensor_group)
        
        sensors = data_group['entities']
        print("SENSORS are sensors", sensors)
        for sensor in sensors:
            sensor_name = sensor['ENTITY_FIELD']['name']
            sensor_type = sensor['ENTITY_FIELD']['type']
            print("SENSORS_NAME", sensor_name)
            values = sensor['TIME_SERIES']
            measurement_units = []
            measurement_ts = []
            measurement_values = []
            for value in values:
                measurement_units.append(value)
                # | !WHY divide by 1000, because 
                # ↓ ValueError: year 57294 is out of range postgres unix time
                measurement_ts.append(values[value]['ts'] / 1000)
                measurement_values.append(values[value]['value'])
            print(sensor_name, "is sensor_type: ", sensor_type)
            print(measurement_units)
            print(measurement_ts)
            print(measurement_values)
            sensor_entry = get_row_by_varchar("sensors", "sensor_name", sensor_name)
            if (sensor_entry == None):
                units_str = ",".join(str(element) for element in measurement_units)
                print("New sensor found! Creating new entry/row in table:sensors, with sensor name: ", sensor_name)
                sensor_entry = create_sensor_entry(get_beehive_for_sensor(sensor_name), sensor_name, sensor_type, units_str, ['2025-04-14', 'YYYY-MM-DD'], measurement_ts[0], True)        
            for unit, ts, value in zip(measurement_units, measurement_ts, measurement_values):
                table_name = sensor_name + "_" +  unit

                data_entry = get_table(table_name)

                print("DATA ENTRY: ", data_entry )
                if (data_entry == False):
                    print("Nothing found! Creating data_entry called ", table_name)
                    print("SENSOR: ", sensor_entry[0])
                    create_data_table(table_name)
                    # TODO insert directly into freshly created table instead of searching again
                    # data_entry = create_data_table(table_name)

                print("Inserting values into table", table_name)
                # TODO insert directly into freshly created table instead of searching again
                insert_values_data(sensor_entry[0], get_beehive_for_sensor(sensor_name), table_name, unit, ts, value)



loop = True
while loop:
    response = fetch_beehive_api_paths()
    if response != None:
        sensor_entities = parse_api_paths(response)
    print("PARSE: ", sensor_entities)
    data = fetch_sensor_groups_data()
    format_for_postgres(data)
    # loop = False
    time.sleep(150)



conn.close()

#.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~  EOF  ~._.~"~.__.~"~._.~"~._.~"~._.~"~._.~"~._.~#