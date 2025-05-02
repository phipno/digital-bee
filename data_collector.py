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


import os
import time
import json
import datetime
import requests

from datetime import datetime
from database_manager import DatabaseManager


class BeehiveDataCollector:
    def __init__(self):
        self.db = DatabaseManager()
        self.api_url = os.getenv('BEEHIVE_API_URL')
        self.api_key = os.getenv('BEEHIVE_API_KEY')
        self.sensor_entities = []
        #Write a funciton for a new sensor addition
        self.sensor_beehive_mapping = [
            {"sensor_name": "LoRa-2CF7F1C0613005BC", "beehive_id": 1},
            {"sensor_name": "LoRa-A840411F645AE815", "beehive_id": 1},
            {"sensor_name": "LoRa-A8404138A188669C", "beehive_id": 2},
            {"sensor_name": "LoRa-A84041892E5A7A68", "beehive_id": 2},
            {"sensor_name": "LoRa-A840419521864618", "beehive_id": 3},
            {"sensor_name": "LoRa-A84041CC625AE81E", "beehive_id": 3}
        ]
        self.initialize_beehives()

    def initialize_beehives(self):
        """Initialize beehive data if not exists"""
        if not self.db.get_row_by_value("beehives", "name", "Larry"):
            self._create_initial_beehives()

    def _create_initial_beehives(self):
        """Create initial beehive entries"""
        beehives = [
            ("Larry", "(49.15182633037482, 9.215298005933729)", "Larry is standing alone, he needs some friends"),
            ("TamTam", "(49.15184249515977, 9.21529330883642)", "TamTam is the middle Sandwhich child"),
            ("BonBon", "(49.151846188225065, 9.215281522540364)", "BonBon is the smallest yet most active")
        ]
        
        for name, location, notes in beehives:
            query = """
            INSERT INTO beehives (name, location, installation_date, last_inspection_date, notes)
            VALUES (%s, %s, TO_DATE(%s, %s), TO_DATE(%s, %s), %s)
            """
            params = (
                name, location, 
                '2025-04-14', 'YYYY-MM-DD',
                '2025-04-14', 'YYYY-MM-DD',
                notes
            )
            self.db.execute_query(query, params)

    def fetch_api_data(self, endpoint):
        """Generic method to fetch API data"""
        try:
            response = requests.get(
                f"{self.api_url}{endpoint}x-apikey={self.api_key}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return None

    def get_sensor_entities(self):
        """Fetch and parse sensor entities from API"""
        response = self.fetch_api_data("?")
        if response:
            self.sensor_entities = [group['authGroupName'] for group in response['authGroup']]
        return self.sensor_entities

    def get_beehive_id_for_sensor(self, sensor_name):
        """Get beehive ID for a given sensor"""
        for mapping in self.sensor_beehive_mapping:
            if mapping["sensor_name"] == sensor_name:
                return mapping["beehive_id"]
        return 0

    def collect_sensor_data(self):
        """Main method to collect and store sensor data"""
        self.get_sensor_entities()
        
        for sensor_group in self.sensor_entities:
            data = self.fetch_api_data(f"/{sensor_group}/entityId?page=0&")
            if data:
                self.process_sensor_data(data['entities'], sensor_group)

    def process_sensor_data(self, sensors, sensor_group):
        """Process and store sensor data"""
        for sensor in sensors:
            sensor_info = sensor['ENTITY_FIELD']
            time_series = sensor['TIME_SERIES']
            
            sensor_name = sensor_info['name']
            beehive_id = self.get_beehive_id_for_sensor(sensor_name)
            
            if not beehive_id:
                print(f"No beehive mapping found for sensor: {sensor_name}")
                continue
                
            self.store_sensor_data(sensor_info, time_series, beehive_id)

    def store_sensor_data(self, sensor_info, time_series, beehive_id):
        """Store sensor data in database"""
        sensor_name = sensor_info['name']
        sensor_type = sensor_info['type']
        
        # Prepare measurement data
        units, timestamps, values = [], [], []
        for metric, data in time_series.items():
            units.append(metric)
            timestamps.append(data['ts'] / 1000)  # Convert to seconds
            values.append(data['value'])
        
        # Check if sensor exists or create new
        sensor_entry = self.db.get_row_by_value("sensors", "sensor_name", sensor_name)
        if not sensor_entry:
            print(f"New sensor found: {sensor_name}")
            sensor_entry = self.create_sensor_entry(
                beehive_id=beehive_id,
                name=sensor_name,
                type=sensor_type,
                units=",".join(units),
                installation_date=['2025-04-14', 'YYYY-MM-DD'],
                last_seen=timestamps[0],
                is_active=True
            )
        
        # Store all measurements
        for unit, ts, value in zip(units, timestamps, values):
            self.insert_measurement(
                sensor_id=sensor_entry[0],
                beehive_id=beehive_id,
                unit=unit,
                timestamp=ts,
                value=value
            )

    def create_sensor_entry(self, beehive_id, name, type, units, installation_date, last_seen, is_active):
        """Create new sensor entry in database"""
        query = """
        INSERT INTO sensors (beehive_id, sensor_name, sensor_type, measurement_units, 
                           installation_date, last_seen, is_active)
        VALUES (%s, %s, %s, %s, TO_DATE(%s, %s), to_timestamp(%s), %s)
        RETURNING *
        """
        params = (
            beehive_id, name, type, units,
            installation_date[0], installation_date[1],
            last_seen, is_active
        )
        return self.db.execute_query(query, params, fetch=True)

    def insert_measurement(self, sensor_id, beehive_id, unit, timestamp, value):
        """Insert measurement data into database"""
        query = """
        INSERT INTO data (sensor_id, beehive_id, measurement_unit, ts, value)
        VALUES (%s, %s, %s, to_timestamp(%s), %s)
        """
        params = (sensor_id, beehive_id, unit, timestamp, value)
        self.db.execute_query(query, params)

    def run(self, interval=600):
        """Main loop to continuously collect data"""
        try:
            while True:
                print("Starting data collection cycle...")
                self.collect_sensor_data()
                print("All Data stored succesfully")
                print(f"Sleeping for {interval} seconds...")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("Stopping data collector...")
        finally:
            self.db.close()


if __name__ == "__main__":
    collector = BeehiveDataCollector()
    collector.run()

#.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~  EOF  ~._.~"~.__.~"~._.~"~._.~"~._.~"~._.~"~._.~#