import csv
from datetime import datetime, timedelta

def is_after(date_str1, date_str2):
    date_str1 = date_str1[:-4]
    date_str2 = date_str2[:-4]
    date1 = datetime.strptime(date_str1, "%H:%M:%S:%f")
    date2 = datetime.strptime(date_str2, "%H:%M:%S:%f")
    return date1 > date2

with open('data/training.data', 'r') as csvfile:
     with open('data/output.data', 'w', newline='') as output_csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        writer = csv.writer(output_csvfile, delimiter=';')
        training_lines = []
        for row in csvreader:
            training_lines.append(row)
        
        last_line = training_lines[0][1]

        for line in training_lines:
            last_hours, last_minutes, last_seconds, _ = last_line.split(":")
            hours, minutes, seconds, _ = line[1].split(":")
            if is_after(line[1], last_line):
                last_line = line[1]
                writer.writerow(line)
        
