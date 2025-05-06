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

###############################################################################
conn_params = {
	"host": "db",
	"port": 5432,
	"dbname": "bee",
	"user": "user",
	"password": "pass"
}
###############################################################################

# def save_to_postgres(entities, conn_params):
# 	conn = psycopg2.connect(**conn_params)
# 	cursor = conn.cursor()

# 	create_table = """
# 	CREATE TABLE IF NOT EXISTS sensor_data (
# 		id UUID,
# 		name TEXT,
# 		type TEXT,
# 		key TEXT,
# 		value TEXT,
# 		timestamp_ms BIGINT,
# 		timestamp_iso TIMESTAMPTZ
# 	)
# 	"""
# 	cursor.execute(create_table)

# 	insert_query = """
# 	INSERT INTO sensor_data (id, name, type, key, value, timestamp_ms, timestamp_iso)
# 	VALUES (%s, %s, %s, %s, %s, %s, %s)
# 	"""

# 	for device in entities:
# 		device_id = device.get("entityId", {}).get("id", "")
# 		device_type = device.get("ENTITY_FIELD", {}).get("type", "")
# 		name = device.get("ENTITY_FIELD", {}).get("name", "")
# 		timeseries = device.get("TIME_SERIES", {})

# 		for key, value in timeseries.items():
# 			raw_ts = value.get("ts")
# 			val = value.get("value")
# 			ts_iso = datetime.fromtimestamp(raw_ts / 1000.0) if raw_ts else None

# 			cursor.execute(insert_query, (
# 				device_id, name, device_type, key, val, raw_ts, ts_iso
# 			))

# 	conn.commit()
# 	cursor.close()
# 	conn.close()
###############################################################################
###############################################################################

def save_to_postgres2(entities, conn_params):
	conn = psycopg2.connect(**conn_params)
	cursor = conn.cursor()

	insert_query = """
	INSERT INTO sensor	 (ID, device_type, device_name)
	VALUES (%s, %s, %s)
	"""

	for device in entities:
		device_id = device.get("entityId", {}).get("id", "")
		device_type = device.get("ENTITY_FIELD", {}).get("type", "")
		device_name = device.get("ENTITY_FIELD", {}).get("name", "")
		timeseries = device.get("TIME_SERIES", {})

		# for key, value in timeseries.items():
		# 	raw_ts = value.get("ts")
		# 	val = value.get("value")
		# 	ts_iso = datetime.fromtimestamp(raw_ts / 1000.0) if raw_ts else None
		cursor.execute(insert_query, (device_id, device_type, device_name))

	conn.commit()
	cursor.close()
	conn.close()
###############################################################################

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
		device_id = device.get("entityId", {}).get("id", "")
		device_type = device.get("ENTITY_FIELD", {}).get("type", "")
		device_name = device.get("ENTITY_FIELD", {}).get("name", "")
		attrs = device.get("SERVER_ATTRIBUTE", {})
		timeseries = device.get("TIME_SERIES", {})

		location = attrs.get("location", {}).get("value", "")

		print(f"Device: {device_name} ({device_type})")
		print(f"  ID: {device_id}")
		print(f"  Location: {location}")

		for key, value in timeseries.items():
			timestamp = value.get('ts')
			time = datetime.fromtimestamp(timestamp / 1000)
			print(f"  {key}: {value.get('value')}) time: {time.strftime("%d/%m/%Y, %H:%M:%S")})")
		print()
	save_to_postgres2(all_entities, conn_params)

###############################################################################

if __name__ == "__main__":
	main()


