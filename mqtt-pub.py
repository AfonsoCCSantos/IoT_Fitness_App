import paho.mqtt.client as mqtt 
import time
import random

broker_hostname = "127.0.0.1"
port = 1883 

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("connected")
    else:
        print("could not connect, return code:", return_code)

client = mqtt.Client("Client1")
# client.username_pw_set(username="user_name", password="password") # uncomment if you use password auth
client.on_connect=on_connect

client.connect(broker_hostname, port)
client.loop_start()

topic = "idc/iris"
msg_count = 0

msg = []
msg.append('[{"model":"iris-KNN"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]')
# msg.append('[{"model":"iris-GNB"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]')
# msg.append('[{"model":"iris-SVC"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]')
# msg.append('[{"model":"iris-DT"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]')
# msg.append('[{"model":"iris-LR"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]')
# msg.append('[{"model":"iris-LDA"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]')

# for i in range(0,50):
#     msg.append(random.randint(0,30)) 

test_topic = "idc/test"
msg_count_test = 0
msg_test = []
msg_test.append('{"analyze": false, "value": 10}')
client.publish(test_topic, msg_test[0])
    
try:
    while msg_count < len(msg):
        time.sleep(3)
        result = client.publish(topic, msg[msg_count])
        status = result[0]
        if status == 0:
            print("Message "+ str(msg[msg_count]) + " is published to topic " + topic)
        else:
            print("Failed to send message to topic " + topic)
        msg_count += 1
finally:
    client.loop_stop()
