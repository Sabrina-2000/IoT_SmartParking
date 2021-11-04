from __future__ import division
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import serial
import time
import threading
device = '/dev/ttyUSB0'
arduino = serial.Serial(device, 9600)
message = ""

def b2_status():
    global message
    if(message[10:14] == "true"):
        arduino.write(b"3")
    elif(message[10:15] == "false"):
        arduino.write(b"4")
        
def power_sensor():
    global message
    if(message[10:14] == "true"):
        arduino.write(b"9")
    elif(message[10:15] == "false"):
        arduino.write(b"10")

def door_sensor():
    global message
    if(message[10:14] == "true"):
        arduino.write(b"1")
    elif(message[10:15] == "false"):
        arduino.write(b"2")

def lockA1():
    global message
    if(message[10:14] == "true"):
        arduino.write(b"5")
    elif(message[10:15] == "false"):
        arduino.write(b"6")

def lockA2():
    global message
    if(message[10:14] == "true"):
        arduino.write(b"7")
    elif(message[10:15] == "false"):
        arduino.write(b"8")        

def on_connect(client, userdata, rc, *extra_params):
    print('Connected with result code' + str(rc))
    client.subscribe('tb/mqtt-integration-guide/sensors/+/rx')

def on_message(client, userdata, msg):
    global message
    print('Incoming message\nTopic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
    message = (msg.payload).decode('UTF-8')
    print(message)
    if(msg.topic.startswith('tb/mqtt-integration-guide/sensors/S1_B2_Status/rx')):
        b2_status()
        
    if(msg.topic.startswith('tb/mqtt-integration-guide/sensors/S1_Power/rx')):
        power_sensor()

    if(msg.topic.startswith('tb/mqtt-integration-guide/sensors/S1_Door/rx')):
        door_sensor()

    if(msg.topic.startswith('tb/mqtt-integration-guide/sensors/S1_Lock_A1/rx')):
        lockA1()

    if(msg.topic.startswith('tb/mqtt-integration-guide/sensors/S1_Lock_A2/rx')):
        lockA2()
    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect('broker.hivemq.com',1883)
client.loop_forever()
#def main():
    #client.loop()