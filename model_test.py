import csv
import joblib
import numpy as np
import pickle
from sklearn.preprocessing import MinMaxScaler

model = joblib.load('cloud-infrastructure/data/app-data/model/classifier.dat.gz')

with open('cloud-infrastructure/data/app-data/data/scaler.pkl', 'rb') as file:
    scaler = pickle.load(file)

print(scaler)

with open('online.data', 'r') as csvfile:
    with open('test.txt', 'w', newline='') as output_csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        writer = csv.writer(output_csvfile)
        for row in csvreader:
            row = [float(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5])]
            row = np.array(row)
            row = row.reshape(1, -1)
            row = scaler.transform(row)
            a = model.predict(row)
            writer.writerow(a)



