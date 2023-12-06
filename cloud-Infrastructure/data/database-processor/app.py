import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/insert', methods=['POST'])
def insert():
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
    acceleration_x = dict['acceleration_x']
    acceleration_y = dict['acceleration_y']
    acceleration_z = dict['acceleration_z']
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
    cursor.execute(insert_data_query, (timestamp, activity_type, acceleration_x, acceleration_y, acceleration_z, gyro_x, gyro_y, gyro_z))
    connection.commit()
    cursor.close()
    connection.close()
    return "Success", 200

@app.route('/select', methods=['POST'])
def select():
    dict = request.get_json()
    if not dict:
        return {
            'error': 'Body is empty.'
        }, 500
    
    connection = psycopg2.connect(
        database="project_db",
        user="group01",
        password="password",
        host="db"
    )
    cursor = connection.cursor()

    if dict['timeOption'] == "day":
        sql_query = """
            SELECT *
            FROM activity
            WHERE DATE(timestamp_column) = %s
        """
        cursor.execute(sql_query, (dict['date'],))
    elif dict['timeOption'] == "week":
        sql_query = """
            SELECT *
            FROM activity
            WHERE EXTRACT(YEAR FROM timestamp_column) = %s
            AND EXTRACT(WEEK FROM timestamp_column) = %s
        """
        cursor.execute(sql_query, (dict["target_year"], dict["target_week"],))
    elif dict['timeOption'] == "month":
        sql_query = """
            SELECT *
            FROM activity
            WHERE EXTRACT(YEAR FROM timestamp_column) = %s
            AND EXTRACT(MONTH FROM timestamp_column) = %s
        """
        cursor.execute(sql_query, (dict["target_year"], dict["target_month"],))
    rows = cursor.fetchall()
    return jsonify(rows)
