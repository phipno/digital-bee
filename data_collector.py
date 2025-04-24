from dotenv import load_dotenv
import os
import requests
import json

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
    for sensor in sensor_entities:
        try:
            response = requests.get(beehive_api_url + "/" + sensor + "/entityId" + "?page=0" + "&x-apikey=" + beehive_api_key)
            response.raise_for_status()
            print(sensor, "\n", response.json())
        except requests.exceptions.RequestException as e:
            print("Error for sensor", sensor , e)



response = fetch_beehive_api_paths()
print("DATA: ", response)
if response != None:
    sensor_entities = parse_api_paths(response)
print("PARSE: ", sensor_entities)
data = fetch_sensor_groups_data()
