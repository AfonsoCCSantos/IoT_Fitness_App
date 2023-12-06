import paho.mqtt.client as mqtt 
import time
import random
import csv
import datetime
import json

broker_hostname = "127.0.0.1"
port = 8883 

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("connected")
    else:
        print("could not connect, return code:", return_code)

client = mqtt.Client("Client1")
client.on_connect=on_connect
client.tls_set(ca_certs="ca.crt",certfile="client.crt",keyfile="client.key")
client.tls_insecure_set(True)
client.connect(broker_hostname, port)
client.loop_start()

topic = "idc/FC01"

msg = []
msg_count = 0
with open('online.data', 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=';')
    for row in csvreader:
        msg.append(row)

try:
    while msg_count < len(msg):
        time.sleep(3)
        row = msg[msg_count]
        current_datetime = datetime.datetime.now()
        date_string = current_datetime.strftime("%m/%d/%y")
        time_string = current_datetime.strftime("%H:%M:%S:%f")[:-3]
        row.append(date_string)
        row.append(time_string)
        json_string = json.dumps(row)
        result = client.publish(topic, json_string)
        status = result[0]
        if status == 0:
            print("Message "+ str(msg[msg_count]) + " is published to topic " + topic)
        else:
            print("Failed to send message to topic " + topic)
        msg_count += 1
finally:
    client.loop_stop()