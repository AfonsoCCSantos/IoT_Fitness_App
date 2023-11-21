import csv
from datetime import datetime, timedelta

def is_after(date_str1, date_str2):
    format_str = "%d/%m/%y %H:%M:%S:%f"
    date_str1 = date_str1[:-4]
    date_str2 = date_str2[:-4]
    date1 = datetime.strptime(date_str1, format_str)
    date2 = datetime.strptime(date_str2, format_str)
    return date1 >= date2

with open('data/training.data', 'r') as csvfile:
     with open('data/output.data', 'w', newline='') as output_csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        writer = csv.writer(output_csvfile, delimiter=';')
        training_lines = []
        for row in csvreader:
            training_lines.append(row)
        
        last_line = training_lines[0][0] + " " + training_lines[0][1]
        
        for line in training_lines:
            formatted_line = line[0] + " " + line[1]
            if is_after(formatted_line, last_line):
                last_line = formatted_line
                writer.writerow(line)
        
