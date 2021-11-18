import serial
import time
import random as r
import drivers
import cv2
import imutils
import time
import numpy as np
import pytesseract
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import smtplib
import MySQLdb
from PIL import Image
from picamera.array import PiRGBArray
from picamera import PiCamera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))
#server=smtplib.SMTP('smtp.gmail.com',587)
#server.starttls()
#server.login('iotsmartparking2021@gmail.com', 'smartparking2021')
device = '/dev/ttyUSB0'
arduino = serial.Serial(device, 9600)
display = drivers.Lcd()
global count, available, slots
action = 0
count = 0
available = 3
slots = ["-","-","-"]
plate = ""
b2status = 0
s1status = "-"
s2status = "-"
emailSend = False
added = False
        
def leaved(plate):
    global count, available, slots, s1status, s2status
    if(slots[0] == plate):
        slots[0] = "-"
        available += 1
        count -= 1
        display.lcd_display_string("Leaved:", 1)
        display.lcd_display_string(str(plate), 2)
        s1status = "-"
        return
    if(slots[1] == plate):
        slots[1] = "-"
        available += 1
        count -= 1
        display.lcd_display_string("Leaved:", 1)
        display.lcd_display_string(str(plate), 2)
        s2status = "-"
        return
    if(slots[2] == plate):
        slots[2] = "-"
        available += 1
        count -= 1
        display.lcd_display_string("Leaved:", 1)
        display.lcd_display_string(str(plate), 2)
        return
    if(slots[0] != "-"):
        booked = slots[0]
        if(booked[:-1] == plate):
            slots[0] = plate
            display.lcd_display_string("Slot:A1", 1)
            display.lcd_display_string(plate, 2)
            return
    if(slots[1] != "-"):
        booked = slots[1]
        if(booked[:-1] == plate):
            slots[1] = plate
            display.lcd_display_string("Slot:A2", 1)
            display.lcd_display_string(plate, 2)
            return
    
def come(plate):
    global count, available, slots

    if(slots[0] == "-"):
        slots[0] = plate
        display.lcd_display_string("Slot:A1", 1)
        available -= 1
        count += 1
        display.lcd_display_string(plate, 2)
        return
        
    elif(slots[1] == "-"):
        slots[1] = plate
        display.lcd_display_string("Slot:A2", 1)
        available -= 1
        count += 1
        display.lcd_display_string(plate, 2)
        return

def capture():
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)
        #key = action
        #if int(key) == 1:
        if key == ord("s"):
             gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #convert to grey scale
             gray = cv2.bilateralFilter(gray, 11, 17, 17) #Blur to reduce noise
             edged = cv2.Canny(gray, 30, 200) #Perform Edge detection
             cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
             cnts = imutils.grab_contours(cnts)
             cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
             screenCnt = None
             for c in cnts:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.018 * peri, True)
                if len(approx) == 4:
                  screenCnt = approx
                  break
             if screenCnt is None:
               detected = 0
               print ("No contour detected")
             else:
               detected = 1
             if detected == 1:
               cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 3)
             mask = np.zeros(gray.shape,np.uint8)
             new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)
             new_image = cv2.bitwise_and(image,image,mask=mask)
             (x, y) = np.where(mask == 255)
             (topx, topy) = (np.min(x), np.min(y))
             (bottomx, bottomy) = (np.max(x), np.max(y))
             Cropped = gray[topx:bottomx+1, topy:bottomy+1]
             text = pytesseract.image_to_string(Cropped, config='--psm 11')
             plate = text[:-2]
             plate = plate.replace(" ","")
             plate = plate.replace("'","")
             plate = plate.replace("(","")
             plate = plate.replace(")","")
             plate = plate.replace(",","")
             plate = plate.replace(".","")
             plate = plate.replace(":","")
             plate = plate.replace(";","")
             print("Detected Number is:",plate)
             cv2.imshow("Frame", image)
             cv2.imshow('Cropped',Cropped)
             time.sleep(2)
             break
    cv2.destroyAllWindows()
    return plate

dbConn = MySQLdb.connect("localhost","pi","","parkingSystem_db") or dle("Could not connect to database") 
print(dbConn)
with dbConn:
    cursor = dbConn.cursor()
    cursor.execute("INSERT INTO record (Counts, Availables, SlotA1, SlotA2, SlotB1) VALUES ('%s','%s','%s','%s','%s')" %(count, available, slots[0], slots[1], slots[2])) 
    dbConn.commit()
    cursor.close()

while True:
    dbConn = MySQLdb.connect("localhost","pi","","parkingSystem_db") or dle("Could not connect to database") 
    with dbConn:
        cursor = dbConn.cursor()
        cursor.execute("SELECT * FROM record")
        dbConn.commit()
        for Id, Counts, Availables, SlotA1, SlotA2, SlotB1 in cursor:
            count = int(Counts)
            available = int(Availables)
            slots[0] = SlotA1
            slots[1] = SlotA2
            slots[2] = SlotB1
        cursor.close()
    
    print("count: " + str(count))
    print("available: " + str(available))
    print(slots[0])
    print(slots[1])
    
    display.lcd_display_string("Available:" + str(available), 1)
    while(arduino.in_waiting == 0):
        dbConn = MySQLdb.connect("localhost","pi","","parkingSystem_db") or dle("Could not connect to database") 
        with dbConn:
            cursor = dbConn.cursor()
            cursor.execute("SELECT * FROM record")
            dbConn.commit()
            for Id, Counts, Availables, SlotA1, SlotA2, SlotB1 in cursor:
                count = int(Counts)
                available = int(Availables)
                slots[0] = SlotA1
                slots[1] = SlotA2
                slots[2] = SlotB1
            cursor.close()
        display.lcd_display_string("Available:" + str(available), 1)
        
        publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(slots[2]) +'}', hostname="thingsboard.cloud", auth = {'username':"nXNiSJDI52nOQqiTy6F0", 'password':""})
        publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(slots[0]) +'}', hostname="thingsboard.cloud", auth = {'username':"4Zdi7c8BlbQB7nL1fLpq", 'password':""})
        publish.single(topic="v1/devices/me/telemetry", payload='{"status":' + str(s1status) +'}', hostname="thingsboard.cloud", auth = {'username':"4Zdi7c8BlbQB7nL1fLpq", 'password':""})
        publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(slots[1]) +'}', hostname="thingsboard.cloud", auth = {'username':"yUYqesVqB0GBThmr1U4h", 'password':""})
        publish.single(topic="v1/devices/me/telemetry", payload='{"status":' + str(s2status) +'}', hostname="thingsboard.cloud", auth = {'username':"yUYqesVqB0GBThmr1U4h", 'password':""})
        publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(available) +'}', hostname="thingsboard.cloud", auth = {'username':"l2W9Yt6qDEhBoTVj1FVB", 'password':""})
        publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(count) +'}', hostname="thingsboard.cloud", auth = {'username':"xHyIFxSBeq87pbF3671m", 'password':""})
        pass

    line = arduino.readline()
    data = line[0:11]
    data = data.decode('UTF-8')

    print(data)
    if(data == "Door Sensor"):
        data = line[13:]
        data = data.decode('UTF-8')
        print(data)
        action = data
        print("Action: " + action)
        
    data = line[0:2]
    data = data.decode('UTF-8')
    
    print(data)
    if(data == "B2"):
        data = line[4:]
        data = data.decode('UTF-8')
        print(data)
        b2status = int(data)
    publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(available) +'}', hostname="thingsboard.cloud", auth = {'username':"l2W9Yt6qDEhBoTVj1FVB", 'password':""})
    publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(count) +'}', hostname="thingsboard.cloud", auth = {'username':"xHyIFxSBeq87pbF3671m", 'password':""})
    
    data = line[0:5]
    data = data.decode('UTF-8')

    print(data)
    if(data == "Slot1"):
        data = line[7:]
        data = data.decode('UTF-8')
        data = data.replace("\r\n", "")
        print(data)
        s1status = data
        publish.single(topic="v1/devices/me/telemetry", payload='{"status":' + str(s1status) +'}', hostname="thingsboard.cloud", auth = {'username':"4Zdi7c8BlbQB7nL1fLpq", 'password':""})
  
    if(data == "Slot2"):
        data = line[7:]
        data = data.decode('UTF-8')
        data = data.replace("\r\n", "")
        print(data)
        s2status = data
        publish.single(topic="v1/devices/me/telemetry", payload='{"status":' + str(s2status) +'}', hostname="thingsboard.cloud", auth = {'username':"yUYqesVqB0GBThmr1U4h", 'password':""})
        
    dbConn = MySQLdb.connect("localhost","pi","","parkingSystem_db") or dle("Could not connect to database") 
    with dbConn:
        cursor = dbConn.cursor()
        cursor.execute("SELECT * FROM record")
        dbConn.commit()
        for Id, Counts, Availables, SlotA1, SlotA2, SlotB1 in cursor:
            count = int(Counts)
            available = int(Availables)
            slots[0] = SlotA1
            slots[1] = SlotA2
            slots[2] = SlotB1
        cursor.close()
    
    #action = "1"
    if(int(action) == 1):
        plate = capture()
        display.lcd_clear()
        
        if(int(b2status) == 1 and slots[2] == "-" and plate != slots[0] and plate != slots[1]):
            slots[2] = plate
            display.lcd_display_string("Slot:B1", 1)
            available -= 1
            count += 1
            display.lcd_display_string(plate, 2)
        elif(slots[0] == plate):
            leaved(plate)
        elif(slots[1] == plate):
            leaved(plate)
        elif(slots[0][:-1] == plate):
            leaved(plate)
        elif(slots[1][:-1] == plate):
            leaved(plate)
        elif(slots[0] == "-"):
            come(plate)
        elif(slots[1] == "-"):
            come(plate)
        else:
            leaved(plate)
        
        print(str(count))
        arduino.write(b"1")
        time.sleep(3)
        arduino.write(b"2")
        time.sleep(1)
        display.lcd_clear()
        action = 0
        
        dbConn = MySQLdb.connect("localhost","pi","","parkingSystem_db") or dle("Could not connect to database") 
        with dbConn:
            cursor = dbConn.cursor()
            cursor.execute("INSERT INTO record (Counts, Availables, SlotA1, SlotA2, SlotB1) VALUES ('%s','%s','%s','%s','%s')" %(count, available, slots[0], slots[1], slots[2])) 
            dbConn.commit()
            cursor.close()
    
    action = 0
    publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(slots[2]) +'}', hostname="thingsboard.cloud", auth = {'username':"nXNiSJDI52nOQqiTy6F0", 'password':""})
    publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(slots[0]) +'}', hostname="thingsboard.cloud", auth = {'username':"4Zdi7c8BlbQB7nL1fLpq", 'password':""})
    publish.single(topic="v1/devices/me/telemetry", payload='{"status":' + str(s1status) +'}', hostname="thingsboard.cloud", auth = {'username':"4Zdi7c8BlbQB7nL1fLpq", 'password':""})
    publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(slots[1]) +'}', hostname="thingsboard.cloud", auth = {'username':"yUYqesVqB0GBThmr1U4h", 'password':""})
    publish.single(topic="v1/devices/me/telemetry", payload='{"status":' + str(s2status) +'}', hostname="thingsboard.cloud", auth = {'username':"yUYqesVqB0GBThmr1U4h", 'password':""})
    publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(available) +'}', hostname="thingsboard.cloud", auth = {'username':"l2W9Yt6qDEhBoTVj1FVB", 'password':""})
    publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(count) +'}', hostname="thingsboard.cloud", auth = {'username':"xHyIFxSBeq87pbF3671m", 'password':""})
    display.lcd_display_string("Available:" + str(available), 1)
    #if(count >= 1 and emailSend == False):
        #server.sendmail('iotsmartparking2021@gmail.com', 'iotsmartparking2021@gmail.com',"Alert!!! Open Basement 2!!!")
        #emailSend = True
        
    #if(count < 1):
        #emailSend = False
      
    
        
        
        

            
