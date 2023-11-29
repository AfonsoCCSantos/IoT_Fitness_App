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

@app.route('/training/<date>/<timeOption>/<walking_thresh>/<running_thresh>', methods=['GET'])
def training(date, timeOption, walking_thresh, running_thresh):
    connection = psycopg2.connect(
        database="project_db",
        user="group01",
        password="password",
        host="db"
    )
    
    cursor = connection.cursor()

    timestamp_seconds = int(date) / 1000.0
    date_object = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
    date_object += timedelta(days=1)

    #Execute the appropriate query, depending on whether the user wants to sort by day,
    #week or month
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
        target_year = date_object.year
        target_month = date_object.month
        sql_query = """
            SELECT *
            FROM activity
            WHERE EXTRACT(YEAR FROM timestamp_column) = %s
            AND EXTRACT(MONTH FROM timestamp_column) = %s
        """
        cursor.execute(sql_query, (target_year, target_month,))

    rows = cursor.fetchall()
    if len(rows) == 0:
        cursor.close()
        connection.close()
        return ""
    
    cursor.close()
    connection.close()
    
    time_walked = 0
    time_run = 0

    first_row_of_activity = rows[0]
    timestamp_datetime = first_row_of_activity[0] #0 is the timestamp column
    seconds_start_of_activity = int(timestamp_datetime.timestamp())

    last_row = first_row_of_activity
    last_row_seconds = seconds_start_of_activity

    activity_type_value = first_row_of_activity[1] #1 is the activity type column

    for row in rows:
        row_timestamp_datetime = row[0]
        current_row_seconds = int(row_timestamp_datetime.timestamp())

        if current_row_seconds - last_row_seconds >= 90:
            if int(last_row[1]) == 0:
                time_walked += last_row_seconds - seconds_start_of_activity
            else:
                time_run += last_row_seconds - seconds_start_of_activity
            seconds_start_of_activity = current_row_seconds 
            activity_type_value = row[1]
        elif row[1] != activity_type_value:
            if int(row[1]) == 0:
                time_run += last_row_seconds - seconds_start_of_activity
            else:
                time_walked += last_row_seconds - seconds_start_of_activity
            seconds_start_of_activity = current_row_seconds 
            activity_type_value = row[1]

        last_row = row
        last_row_seconds = current_row_seconds    
    
    final_row = rows[-1]
    final_row_timestamp_datetime = final_row[0]
    final_row_seconds = int(final_row_timestamp_datetime.timestamp())

    if activity_type_value == 0:
        time_walked += final_row_seconds - seconds_start_of_activity
    else:
        time_run += final_row_seconds - seconds_start_of_activity

    #Assuming the user is a male 20-29yo, 1.80m, 75kg
    #Assuming the user is a male 20-29yo, 1.80m, 75kg
    calories_burned_walking_permin = 0.035 * 75 + ((1.36**2) / 1.80) * 0.029 * 75
    calories_burned_running_permin = 0.035 * 75 + ((2.72**2) / 1.80) * 0.029 * 75
    distance_walked = (1.36 * time_walked) / 1000 #distance in kms
    distance_run = (1.36 * 2 * time_run) / 1000 #distance in kms

    calories_burned_running = (time_run / 60) * calories_burned_running_permin
    calories_burned_walking = (time_walked / 60) * calories_burned_walking_permin
    total_time_activity = time_run + time_walked

    walking_thresh = int(walking_thresh)
    running_thresh = int(running_thresh)
    if timeOption == "Week":
        walking_thresh = walking_thresh * 7
        running_thresh = running_thresh * 7
    elif timeOption == "Month":
        walking_thresh = walking_thresh * 30
        running_thresh = running_thresh * 30
    
    active = False
    if time_run >= running_thresh and time_walked >= walking_thresh:
        active = True

    result_dict = {
        "distance_walking": distance_walked,
        "distance_running": distance_run,
        "calories_burned_running": calories_burned_running,
        "calories_burned_walking": calories_burned_walking,
        "time_running": time_run,
        "time_walking": time_walked,
        "total_time_activity": total_time_activity,
        "active": active
    }
    return result_dict, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0')
