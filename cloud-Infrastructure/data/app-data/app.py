# Local imports
import datetime

# Third part imports
from flask import Flask, request, jsonify
import pandas as pd
import requests
import joblib
import psycopg2
import pickle
import numpy as np
import os
import functions

from datetime import datetime, timedelta, timezone

with open('data/scaler.pkl', 'rb') as file:
    scaler = pickle.load(file)
model = joblib.load('model/classifier.dat.gz')

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Return service health"""
    return 'ok'

@app.route('/predict', methods=['POST'])
def predict():
    dict = request.get_json()
    if not dict:
        return {
            'error': 'Body is empty.'
        }, 500
    data = [float(dict['acceleration_x']), float(dict['acceleration_y']), float(dict['acceleration_z']), float(dict['gyro_x']), float(dict['gyro_y']), float(dict['gyro_z'])]
    data = np.array(data)
    data = data.reshape(1, -1)
    data = scaler.transform(data)
    response = model.predict(data)

    age = int(dict['age'])
    height = float(dict['height'])
    gender = dict['gender']
    weight = float(dict['weight'])
    velocity = float(functions.determine_velocity(age, gender))

    if response == 0:
        response = 'walking'
    else:
        response = 'running'

    if not os.path.exists('data/activity.txt'):
        with open('data/activity.txt', 'w') as file:
            #file = dist_walk/dist_run/cal_run/cal_walk/time_run/time_walk
            file.write(f'{0}/{0}/{0}/{0}/{0}/{0}')
        result = {
            "distance_walking": 0,
            "distance_running": 0,
            "calories_burned_running": 0,
            "calories_burned_walking": 0,
            "time_running": 0,
            "time_walking": 0,
            "activity": 0
        }
        return result, 200
    else:
        with open('data/activity.txt', 'r') as file:
            line = file.readline()
            data = line.split('/')
        with open('data/activity.txt', 'w') as file:
            #We know that we receive new data every 1 second
            distance_walked = float(data[0])
            distance_run = float(data[1])
            calories_burned_running = float(data[2])
            calories_burned_walking = float(data[3])
            time_running = int(data[4])
            time_walking = int(data[5])
            if response == "walking":
                distance_walked_tmp = (velocity / 1000)
                calories_burned_walking_permin = 0.035 * weight + ((velocity**2) / height) * 0.029 * weight
                calories_burned_walking_tmp = (1 / 60) * calories_burned_walking_permin
                calories_burned_walking += calories_burned_walking_tmp
                distance_walked += distance_walked_tmp
                time_walking += 1
            else:
                distance_run_tmp = (velocity * 2) / 1000 #distance in kms
                calories_burned_running_permin = 0.035 * weight + (((velocity*2)**2) / height) * 0.029 * weight
                calories_burned_running_tmp = (1 / 60) * calories_burned_running_permin
                calories_burned_running += calories_burned_running_tmp
                distance_run += distance_run_tmp
                time_running += 1
            file.write(f'{distance_walked}/{distance_run}/{calories_burned_running}/{calories_burned_walking}/{time_running}/{time_walking}')
            result = {
                "distance_walking": distance_walked,
                "distance_running": distance_run,
                "calories_burned_running": calories_burned_running,
                "calories_burned_walking": calories_burned_walking,
                "time_running": time_running,
                "time_walking": time_walking,
                "activity": response
            }
    return result, 200

@app.route('/training/<date>/<timeOption>/<running_thresh>/<walking_thresh>/<age>/<gender>/<height>/<weight>', methods=['GET'])
def training(date, timeOption, running_thresh, walking_thresh, age, gender, height, weight):
    timestamp_seconds = int(date) / 1000.0
    date_object = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
    date_object += timedelta(days=1)
    urlSelect = 'http://databaseprocessor:8500/select'

    timeOption = timeOption.lower()
    if timeOption == "day":
        formatted_target_date = date_object.strftime('%Y-%m-%d')
        jsonData = {
            "timeOption": timeOption,
            "date": formatted_target_date
        }
    elif timeOption == "week":
        target_year, target_week, _ = date_object.isocalendar()
        jsonData = {
            "timeOption": timeOption,
            "target_year": target_year,
            "target_week": target_week
        }
    elif timeOption == "month":
        target_year = date_object.year
        target_month = date_object.month
        jsonData = {
            "timeOption": timeOption,
            "target_year": target_year,
            "target_month": target_month
        }
    response = requests.post(urlSelect, json=jsonData)
    rows = response.json()

    if len(rows) == 0:
        result_dict = {
            "distance_walking": 0,
            "distance_running": 0,
            "calories_burned_running": 0,
            "calories_burned_walking": 0,
            "time_running": 0,
            "time_walking": 0,
            "total_time_activity": 0,
            "active": False,
            "timeOption": timeOption
        }
        return result_dict, 200
    
    time_walked = 0
    time_run = 0

    first_row_of_activity = rows[0]
    timestamp_datetime = first_row_of_activity[0] #0 is the timestamp column
    parsed_date = datetime.strptime(timestamp_datetime, "%a, %d %b %Y %H:%M:%S GMT")
    seconds_start_of_activity = int(parsed_date.timestamp())

    last_row = first_row_of_activity
    last_row_seconds = seconds_start_of_activity

    activity_type_value = first_row_of_activity[1] #1 is the activity type column

    for row in rows:
        row_timestamp_datetime = row[0]
        parsed_date = datetime.strptime(row_timestamp_datetime, "%a, %d %b %Y %H:%M:%S GMT")
        current_row_seconds = int(parsed_date.timestamp())

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
    parsed_date = datetime.strptime(final_row_timestamp_datetime, "%a, %d %b %Y %H:%M:%S GMT")
    final_row_seconds = int(parsed_date.timestamp())

    if activity_type_value == 0:
        time_walked += final_row_seconds - seconds_start_of_activity
    else:
        time_run += final_row_seconds - seconds_start_of_activity

    weight = float(weight)
    height = float(height)
    velocity = float(functions.determine_velocity(age, gender))
    calories_burned_walking_permin = 0.035 * weight + ((velocity**2) / height) * 0.029 * weight
    calories_burned_running_permin = 0.035 * weight + (((velocity*2)**2) / height) * 0.029 * weight
    distance_walked = (1.36 * time_walked) / 1000 #distance in kms
    distance_run = (1.36 * 2 * time_run) / 1000 #distance in kms

    calories_burned_running = (time_run / 60) * calories_burned_running_permin
    calories_burned_walking = (time_walked / 60) * calories_burned_walking_permin
    total_time_activity = time_run + time_walked
    
    if timeOption == "Week":
        walking_thresh  = walking_thresh * 7
        running_thresh = running_thresh * 7
    elif timeOption == "Month":
        walking_thresh  = walking_thresh * 30
        running_thresh = running_thresh * 30
    
    active = False
    if time_run >= int(running_thresh) and time_walked >= int(walking_thresh):
        active = True

    result_dict = {
        "distance_walking": distance_walked,
        "distance_running": distance_run,
        "calories_burned_running": calories_burned_running,
        "calories_burned_walking": calories_burned_walking,
        "time_running": time_run,
        "time_walking": time_walked,
        "total_time_activity": total_time_activity,
        "active": active,
        "timeOption": timeOption
    }
    return result_dict, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0')
