from datetime import datetime, timedelta, timezone
import psycopg2

timestamp_seconds = 1688166000000 / 1000.0
date_object = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
date_object += timedelta(days=1)

target_year, target_week, _ = date_object.isocalendar()

formatted_target_date = date_object.strftime('%Y-%m-%d')

connection = psycopg2.connect(
    database="project_db",
    user="group01",
    password="password",
    host="localhost"
)

cursor = connection.cursor()

sql_query = """
    SELECT *
    FROM activity
    WHERE DATE(timestamp_column) = %s
"""

cursor.execute(sql_query, (formatted_target_date,))

rows = cursor.fetchall()

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

    if current_row_seconds - last_row_seconds >= 500:
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


print(time_walked)
print(time_run)

#---------------------------------------





















