import psycopg2
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/insert', methods=['POST'])
def predict():
    dict = request.get_json()
    if not dict:
        return {
            'error': 'Body is empty.'
        }, 500
    insert_data_query = '''
    INSERT INTO activity 
    (timestamp_column, activity_type, acceleration_x, acceleration_y, acceleration_z, gyro_x, gyro_y, gyro_z)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    '''
    timestamp = dict['timestamp']
    activity_type = dict['activity_type']
    accelaration_x = dict['accelaration_x']
    accelaration_y = dict['accelaration_y']
    accelaration_z = dict['accelaration_z']
    gyro_x = dict['gyro_x']
    gyro_y = dict['gyro_y']
    gyro_z = dict['gyro_z']

    connection = psycopg2.connect(
        database="project_db",
        user="group01",
        password="password",
        host="db"
    )
    cursor = connection.cursor()
    cursor.execute(insert_data_query, (timestamp, activity_type, accelaration_x, accelaration_y, accelaration_z, gyro_x, gyro_y, gyro_z))
    connection.commit()
    return "Success", 200