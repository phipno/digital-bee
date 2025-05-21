# *--------------------------------------------------------------------------------------*#
# *                                                                                .|    *#
# *     $FILENAME                      dashboard.py    /     (__)          |/            *#
# *                                                          (oo)------/'   ,__,    ,    *#
# *     By: $AUTHOR                          phipno       |  (__)     ||    (oo)_____/   *#
# *                                                             ||---/||    (__)    ||   *#
# *     Created: $CREATEDAT 2025.04.29    by phipno   |/                  ,    ||--w||   *#
# *                                                  ,,       !              |'          *#
# *                                                       ,           ,|             |/  *#
# *----------------8<------------------[ mooooooo ]--------------------------------------*#
from flask import Flask, render_template, jsonify
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timezone
import os
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Database connection
def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv('DB_HOST'), # If hosted publicly
            # host=os.getenv('PG_HOST'), # Good for debugging locally
            # host=os.getenv('localhost'), # If hosted locally
            database=os.getenv('DB_NAME'),
            # database=os.getenv('PG_NAME'),
            user=os.getenv('DB_USER'),
            # user=os.getenv('PG_USER'),
            password=os.getenv('DB_PASSWORD'),
            # password=os.getenv('PG_PASSWORD'),
            port=os.getenv('DB_PORT'),
            # port=os.getenv('PG_PORT'),
            connect_timeout=3,
            application_name="dashboard"  # Add this identifier
        )
    except psycopg2.Error as e:
        print(f"Connection failed: {e}")
        raise
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/beehives')
def get_beehives():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM beehives")
    beehives = cursor.fetchall()
    
    # Convert to list of dictionaries
    beehive_list = []
    for beehive in beehives:
        beehive_list.append({
            'id': beehive[0],
            'name': beehive[1],
            'location': beehive[2],
            'installation_date': beehive[3].strftime('%Y-%m-%d'),
            'last_inspection_date': beehive[4].strftime('%Y-%m-%d') if beehive[4] else None,
            'notes': beehive[5]
        })
    
    cursor.close()
    conn.close()
    
    return jsonify(beehive_list)

@app.route('/api/sensors')
def get_sensors():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sensors")
    sensors = cursor.fetchall()
    
    # Convert to list of dictionaries
    sensor_list = []
    for sensor in sensors:
        sensor_list.append({
            'id': sensor[0],
            'beehive_id': sensor[1],
            'name': sensor[2],
            'type': sensor[3],
            'units': sensor[4],
            'last_seen': sensor[6].strftime('%Y-%m-%d %H:%M:%S'),
            'active': sensor[7]
        })
    
    cursor.close()
    conn.close()
    
    return jsonify(sensor_list)

@app.route('/api/sensors_by_id/<sensor_id>')
def get_sensors_by_sensor_id(sensor_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM sensors WHERE sensor_id = %s", (sensor_id,))
        sensors = cursor.fetchall()
        
        # Convert to list of dictionaries
        sensor_list = []
        for sensor in sensors:
            sensor_list.append({
                'id': sensor[0],
                'beehive_id': sensor[1],
                'name': sensor[2],
                'type': sensor[3],
                'units': sensor[4],
                'last_seen': sensor[6].strftime('%Y-%m-%d %H:%M:%S'),
                'active': sensor[7]
            })
        return jsonify(sensor_list)
    
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/sensors_by_beehive/<beehive_id>')
def get_sensors_by_beehive(beehive_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM sensors WHERE beehive_id = %s", (beehive_id,))
        sensors = cursor.fetchall()
        
        # Convert to list of dictionaries
        sensor_list = []
        for sensor in sensors:
            sensor_list.append({
                'id': sensor[0],
                'beehive_id': sensor[1],
                'name': sensor[2],
                'type': sensor[3],
                'units': sensor[4],
                'last_seen': sensor[6].strftime('%Y-%m-%d %H:%M:%S'),
                'active': sensor[7]
            })
        print(sensor_list)
        return jsonify(sensor_list)
    
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

def convertTime(date_input):
    dt_gmt = date_input.replace(tzinfo=timezone.utc)
    # Convert to local timezone
    local_tz = pytz.timezone("Europe/Berlin")
    dt_local = dt_gmt.astimezone(local_tz)
    # Format back to string
    return dt_local.strftime('%Y-%m-%d %H:%M:%S')


@app.route('/api/sensor_data_by_beehive/<beehive_id>/<unit>/<hours>')
def get_data_in_beehive_hours(beehive_id, unit, hours):
    conn = get_db_connection()
    cursor = conn.cursor()

    time_threshold = datetime.now() - timedelta(hours=int(hours))
    try:
        cursor.execute(
            f"SELECT ts, value FROM data WHERE ts >= %s AND beehive_id = %s AND measurement_unit = %s ORDER BY ts",
            (time_threshold, beehive_id, unit)
        )
        data = cursor.fetchall()
        
        # Convert to list of dictionaries
        data_list = []
        for row in data:
            data_list.append({
                'timestamp': convertTime(row[0]),
                'value': row[1]
            })
        return jsonify(data_list)
    
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/sensor_data_timeframe/<sensor_id>/<unit>/<starttime>/<endtime>')
def get_data_sensor_timefame(sensor_id, unit, starttime, endtime):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    time_threshold = datetime.now() - timedelta(24)
    print("Starttime is:",starttime)
    print("Endtime is:",endtime)

    try:
        cursor.execute(
            f"SELECT ts, value FROM data WHERE ts >= %s AND sensor_id = %s AND measurement_unit = %s ORDER BY ts",
            (time_threshold, sensor_id, unit)
        )
        data = cursor.fetchall()
        
        # Convert to list of dictionaries
        data_list = []
        for row in data:
            data_list.append({
                'timestamp': convertTime(row[0]),
                'value': row[1]
            })
        return jsonify(data_list)
    
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/sensor_data/<sensor_id>/<unit>/<hours>')
def get_data_sensor_hours(sensor_id, unit, hours):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    time_threshold = datetime.now() - timedelta(hours=int(hours))
    try:
        cursor.execute(
            f"SELECT ts, value FROM data WHERE ts >= %s AND sensor_id = %s AND measurement_unit = %s ORDER BY ts",
            (time_threshold, sensor_id, unit)
        )
        data = cursor.fetchall()
        
        # Convert to list of dictionaries
        data_list = []
        for row in data:
            data_list.append({
                'timestamp': convertTime(row[0]),
                'value': row[1]
            })
        return jsonify(data_list)
    
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
