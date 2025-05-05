from dotenv import load_dotenv
import requests
import os
# import json
import urllib.parse
import matplotlib.pyplot as plt
from datetime import datetime



load_dotenv()

weather_api_url = os.getenv('WEATHER_API_URL')
weather_api_key = os.getenv('WEATHER_API_KEY')

beehive_api_url = os.getenv('BEEHIVE_API_URL')
beehive_api_key = os.getenv('BEEHIVE_API_KEY')


def get_auth_groups():
	url = beehive_api_url + "?x-apikey=" + beehive_api_key
	# response = requests.get(beehive_api_url, params=params)
	response = requests.get(url)
	# response.raise_for_status() #?
	return response.json()["authGroup"]
	
	


def get_entities_for_authgroup(group):
	url = f"{beehive_api_url}/{group}/entityId" + "?page=0" + "&x-apikey=" + beehive_api_key
	# print(url)
	response = requests.get(url)
	# response.raise_for_status() #?
	return response.json()



def main():
	all_entities = []
	auth_groups = get_auth_groups()
	# print(auth_groups)
	for group in auth_groups:
		name = group["authGroupName"]
		entities = get_entities_for_authgroup(name)
		# print(entities)
		all_entities.extend(entities["entities"])
	for device in all_entities:
		entity_id = device.get("entityId", {}).get("id", "")
		entity_type = device.get("ENTITY_FIELD", {}).get("type", "")
		name = device.get("ENTITY_FIELD", {}).get("name", "")
		attrs = device.get("SERVER_ATTRIBUTE", {})
		timeseries = device.get("TIME_SERIES", {})

		# latitude = attrs.get("latitude", {}).get("value", "")
		# longitude = attrs.get("longitude", {}).get("value", "")
		location = attrs.get("location", {}).get("value", "")

		print(f"Device: {name} ({entity_type})")
		print(f"  ID: {entity_id}")
		print(f"  Location: {location}")

		for key, value in timeseries.items():
			timestamp = value.get('ts')
			time = datetime.fromtimestamp(timestamp / 1000)
			print(f"  {key}: {value.get('value')})") (time: {time.strftime("%d/%m/%Y, %H:%M:%S")})")
		print()

if __name__ == "__main__":
	main()


