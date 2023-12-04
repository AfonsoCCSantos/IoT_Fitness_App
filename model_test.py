import csv
import joblib
import numpy as np

model = joblib.load('cloud-infrastructure/data/app-data/model/classifier.dat.gz')

with open('online.data', 'r') as csvfile:
    with open('test.txt', 'w', newline='') as output_csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        writer = csv.writer(output_csvfile)
        for row in csvreader:
            row = [float(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5])]
            row = np.array(row)
            row = row.reshape(1, -1)
            a = model.predict(row)
            writer.writerow(a)



