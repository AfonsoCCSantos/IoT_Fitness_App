import csv
import psycopg2
from datetime import datetime

# Establish a connection to the PostgreSQL server
connection = psycopg2.connect(
    database="project_db",
    user="group01",
    password="password",
    host="localhost"
)

try:
    # Create a cursor object to interact with the database
    with connection.cursor() as cursor:
        # Example query
        cursor.execute("DROP TABLE IF EXISTS activity")
        cursor.execute("CREATE TABLE activity (timestamp_column TIMESTAMP PRIMARY KEY, activity_type INTEGER, acceleration_x DECIMAL, acceleration_y DECIMAL, acceleration_z DECIMAL, gyro_x DECIMAL, gyro_y DECIMAL, gyro_z DECIMAL)")
        # Read data from CSV file and insert into the table
        with open('data/training.data', 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';')
            for row in csvreader:
                # Parse the data
                date, time, activity_type, acceleration_x, acceleration_y, acceleration_z, gyro_x, gyro_y, gyro_z = row
                date = datetime.strptime(date, "%d/%m/%y")
                date = date.strftime("%m/%d/20%y")
                timestamp = datetime.strptime(date + ' ' + time[:-4], '%m/%d/20%y %H:%M:%S:%f')
                # Insert data into the table
                insert_data_query = '''
                INSERT INTO activity 
                (timestamp_column, activity_type, acceleration_x, acceleration_y, acceleration_z, gyro_x, gyro_y, gyro_z)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                '''
                cursor.execute(insert_data_query, (timestamp, int(activity_type), float(acceleration_x), float(acceleration_y), float(acceleration_z), float(gyro_x), float(gyro_y), float(gyro_z)))
    connection.commit()  
finally:
    # Close the connection
    cursor.close()
    connection.close()

#date;time;activity;acceleration_x;acceleration_y;acceleration_z;gyro_x;gyro_y;gyro_z