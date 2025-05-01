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
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        database=os.getenv('DB_NAME'),
        # host=os.getenv('DB_HOST'),
        host='localhost',
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT')
    )
    return conn

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

@app.route('/api/sensor_data/<sensor_id>/<beehive_id>/<unit>/<hours>')
def get_sensor_dat(sensor_id, beehive_id, unit, hours):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    time_threshold = datetime.now() - timedelta(hours=int(hours))
    try:
        cursor.execute(
            f"SELECT ts, value FROM data WHERE ts >= %s AND sensor_id = %s ORDER BY ts",
            (time_threshold, sensor_id)
        )
        data = cursor.fetchall()
        
        # Convert to list of dictionaries
        data_list = []
        for row in data:
            data_list.append({
                'timestamp': row[0].strftime('%Y-%m-%d %H:%M:%S'),
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