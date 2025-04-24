from dotenv import load_dotenv
import os
import requests
import json
import datetime
import time

load_dotenv()

beehive_api_url = os.getenv('BEEHIVE_API_URL')
beehive_api_key = os.getenv('BEEHIVE_API_KEY')

wather_api_url = os.getenv('WEATHER_API_URL')
wather_api_url = os.getenv('WEATHER_API_KEY')

sensor_entities = []

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
    

def format_for_postgres(data):
    """For later parsing to postgres"""
    for data_group, sensor_group in zip(data, sensor_entities):
        print(sensor_group, " ", sensor_group, " ", sensor_group)
        
        sensors = data_group['entities']
        # print(sensors)
        for sensor in sensors:
            sensor_name = sensor['ENTITY_FIELD']['name']
            sensor_type = sensor['ENTITY_FIELD']['type']
            values = sensor['TIME_SERIES']
            measurement_units = []
            measurement_ts = []
            measurement_values = []
            for value in values:
                measurement_units.append(value)
                measurement_ts.append(values[value]['ts'])
                measurement_values.append(values[value]['value'])
            print(sensor_name, "is sensor_type: ", sensor_type)
            print(measurement_units)
            print(measurement_ts)
            print(measurement_values)
            #TODO create function that creates postgres entries for each sensor
            #TODO create function that creates postgres entries for each measurement_units



response = fetch_beehive_api_paths()
if response != None:
    sensor_entities = parse_api_paths(response)
print("PARSE: ", sensor_entities)
data = fetch_sensor_groups_data()
format_for_postgres(data)