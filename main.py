from dotenv import load_dotenv
import requests
import os
# import json
# import urllib.parse

from datetime import datetime

import psycopg2


load_dotenv()

weather_api_url = os.getenv('WEATHER_API_URL')
weather_api_key = os.getenv('WEATHER_API_KEY')

beehive_api_url = os.getenv('BEEHIVE_API_URL')
beehive_api_key = os.getenv('BEEHIVE_API_KEY')

###############################################################################

def get_auth_groups():
	url = beehive_api_url + "?x-apikey=" + beehive_api_key
	# response = requests.get(beehive_api_url, params=params)
	response = requests.get(url)
	# response.raise_for_status() #?
	return response.json()["authGroup"]
	
	
###############################################################################


def get_entities_for_authgroup(group):
	url = f"{beehive_api_url}/{group}/entityId" + "?page=0" + "&x-apikey=" + beehive_api_key
	# print(url)
	response = requests.get(url)
	# response.raise_for_status() #?
	return response.json()


###############################################################################

conn_params = {
	"host": "db",
	"port": 5432,
	"dbname": "bee",
	"user": "user",
	"password": "pass"
}

###############################################################################

def saveToPostgres_location(location):
	conn = psycopg2.connect(**conn_params)
	cursor = conn.cursor()

	print(f"  Location: {location}✅")

	insert_query = """
	INSERT INTO location (ID, location_name)
	VALUES (%s, %s)
	ON CONFLICT (ID) DO NOTHING
	"""

	cursor.execute(insert_query, (1, location))

	conn.commit()
	cursor.close()
	conn.close()

###############################################################################
def saveToPostgres_devices(device):
	conn = psycopg2.connect(**conn_params)
	cursor = conn.cursor()

	device_id = device.get("entityId", {}).get("id", "")
	device_type = device.get("ENTITY_FIELD", {}).get("type", "")
	device_name = device.get("ENTITY_FIELD", {}).get("name", "")

	print(f"Device: {device_name} ({device_type})✅")
	print(f"  ID: {device_id}✅")
	
	insert_query = """
	INSERT INTO sensor	 (ID, device_type, device_name)
	VALUES (%s, %s, %s)
	ON CONFLICT (ID) DO NOTHING
	"""

	cursor.execute(insert_query, (device_id, device_type, device_name))

	conn.commit()
	cursor.close()
	conn.close()

###############################################################################

def saveToPostgres_data(timeseries):
	conn = psycopg2.connect(**conn_params)
	cursor = conn.cursor()

	unit_map = {
		"lightIntensity": "%",
		"rainGauge": "?",
		"relativeHumidity": "%"+ "rF",
		"temperature": "°C",
		"tempC1": "°C",
		"tempC2": "°C",
		"tempC3": "°C",
		"pressure": "hPa",
		"windDirection": "NSOW",
		"uvIndex": "UVI",
		"windSpeed": "km/h",
	}

	for key, list in timeseries.items():
		timestamp = list.get('ts')
		time = datetime.fromtimestamp(timestamp / 1000)
		print(f"  {key}✅: {list.get('value')}❌ time: {time.strftime("%d/%m/%Y, %H:%M:%S")}❌")
		name = key

		unit = ""
		for u in unit_map:
			if u.lower() in name.lower():
				# print(f"Found unit: {u} => {unit_map[u]}")
				unit = unit_map[u]
				break

		insert_query = """
		INSERT INTO measurement_type (name, unit)
		VALUES (%s, %s)
		ON CONFLICT (name) DO NOTHING
		"""
		cursor.execute(insert_query, (name, unit))

		value = list.get('value')
		t = time.strftime("%d/%m/%Y, %H:%M:%S")
		
		insert_query = """
		INSERT INTO data (value, time)
		VALUES (%s, %s)
		"""
		cursor.execute(insert_query, (value, t))

	conn.commit()
	cursor.close()
	conn.close()

###############################################################################

def main():
	all_entities = []
	auth_groups = get_auth_groups()
	print(auth_groups)
	for group in auth_groups:
		name = group["authGroupName"]
		entities = get_entities_for_authgroup(name)
		# print(entities)
		all_entities.extend(entities["entities"])
	for device in all_entities:
		saveToPostgres_devices(device)

		attrs = device.get("SERVER_ATTRIBUTE", {})
		location = attrs.get("location", {}).get("value", "")
		saveToPostgres_location(location)


		timeseries = device.get("TIME_SERIES", {})
		saveToPostgres_data(timeseries)

###############################################################################

if __name__ == "__main__":
	main()
