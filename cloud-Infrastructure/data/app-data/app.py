# Local imports
import datetime

# Third part imports
from flask import Flask
from flask import request
import pandas as pd
import joblib
import psycopg2

from modules.functions import get_model_response
from datetime import datetime, timedelta, timezone


app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health():
    """Return service health"""
    return 'ok'


@app.route('/predict', methods=['POST'])
def predict():
    feature_dict = request.get_json()
    if not feature_dict:
        return {
            'error': 'Body is empty.'
        }, 500
    
    try:
        data = []
        model_name = feature_dict[0]['model']
        model = joblib.load('model/' + model_name + '.dat.gz')
        data.append(feature_dict[1])
        response = get_model_response(data, model)
    except ValueError as e:
        return {'error': str(e).split('\n')[-1].strip()}, 500

    return response, 200

@app.route('/training/<date>/<timeOption>', methods=['GET'])
def training(date, timeOption):
    connection = psycopg2.connect(
        database="project_db",
        user="group01",
        password="password",
        host="localhost"
    )
    cursor = connection.cursor()

    timestamp_seconds = date / 1000.0
    date_object = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
    date_object += timedelta(days=1)

    if timeOption == "Day":
        formatted_target_date = date_object.strftime('%Y-%m-%d')
        sql_query = """
            SELECT *
            FROM activity
            WHERE DATE(timestamp_column) = %s
        """
        cursor.execute(sql_query, (formatted_target_date,))

    elif timeOption == "Week":
        target_year, target_week, _ = date_object.isocalendar()
        sql_query = """
            SELECT *
            FROM activity
            WHERE EXTRACT(YEAR FROM timestamp_column) = %s
            AND EXTRACT(WEEK FROM timestamp_column) = %s
        """
        cursor.execute(sql_query, (target_year, target_week,))
    
    elif timeOption == "Month":
        target_month = date_object.month
        sql_query = """
            SELECT *
            FROM your_table
            WHERE EXTRACT(YEAR FROM your_timestamp_column) = %s
            AND EXTRACT(MONTH FROM your_timestamp_column) = %s
        """
        cursor.execute(sql_query, (target_year, target_month,))

    rows = cursor.fetchall()
    
    time_walked = 0
    time_run = 0

    first_row_of_activity = rows[0]
    timestamp_string = first_row_of_activity['timestamp_column']
    timestamp_datetime = datetime.strptime(timestamp_string, '%Y-%m-%d %H:%M:%S.%f')
    seconds_start_of_activity = int(timestamp_datetime.timestamp())

    activity_type_value = first_row_of_activity['activity_type']

    for row in rows:
        if row['activity_type'] != activity_type_value:
            row_timestamp_string = row['timestamp_column']
            row_timestamp_datetime = datetime.strptime(row_timestamp_string, '%Y-%m-%d %H:%M:%S.%f')
            seconds_end_of_activity = int(row_timestamp_datetime.timestamp())

            if int(row['activity_type']) == 0:
                time_walked += seconds_end_of_activity - seconds_start_of_activity
            else:
                time_run += seconds_end_of_activity - seconds_start_of_activity

            seconds_start_of_activity = seconds_end_of_activity 
    
    return date_object, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0')
