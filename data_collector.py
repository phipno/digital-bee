from dotenv import load_dotenv
import os
import requests

load_dotenv()

beehive_api_url = os.getenv('BEEHIVE_API_URL')
beehive_api_key = os.getenv('BEEHIVE_API_KEY')

wather_api_url = os.getenv('WEATHER_API_URL')
wather_api_url = os.getenv('WEATHER_API_KEY')

def fetch_beehive_data():
    """Fetch data from the sensor API"""
    headers = {'Authorization': f'Bearer {beehive_api_key}'}
    try:
        response = requests.get(beehive_api_url + beehive_api_key)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error", e)
        return None

print("DATA: ", fetch_beehive_data())