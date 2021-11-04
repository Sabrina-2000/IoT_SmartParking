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
from PIL import Image
from picamera.array import PiRGBArray
from picamera import PiCamera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))
server=smtplib.SMTP('smtp.gmail.com',587)
server.starttls()
server.login('iotsmartparking2021@gmail.com', 'smartparking2021')

device = '/dev/ttyUSB0'
arduino = serial.Serial(device, 9600)
display = drivers.Lcd()
action = "0"
count = 0
available = 3
slots = ["-","-","-"]
plate = ""
b2status = 0
emailSend = False

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
             print("Detected Number is:",text[:-2])
             plate = text[:-2]
             cv2.imshow("Frame", image)
             cv2.imshow('Cropped',Cropped)
             time.sleep(2)
             break
    cv2.destroyAllWindows()
    return plate


while True:
    display.lcd_display_string("Available:" + str(available), 1)
    while(arduino.in_waiting == 0):
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
    
    #action = "1"
    if(int(action) == 1):
        plate = capture()
        plate = plate.replace(" ","")
        
        display.lcd_clear()
        if(slots[0] == plate):
            slots[0] = "-"
            available += 1
            count -= 1
            publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(slots[0]) +'}', hostname="thingsboard.cloud", auth = {'username':"4Zdi7c8BlbQB7nL1fLpq", 'password':""})
                
        elif(slots[1] == plate):
            slots[1] = "-"
            available += 1
            count -= 1
            publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(slots[1]) +'}', hostname="thingsboard.cloud", auth = {'username':"yUYqesVqB0GBThmr1U4h", 'password':""})
             
        elif(slots[2] == plate):
            slots[2] = "-"
            available += 1
            count -= 1
            publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(slots[1]) +'}', hostname="thingsboard.cloud", auth = {'username':"nXNiSJDI52nOQqiTy6F0", 'password':""})
        
        elif(int(b2status) == 1 and slots[2] == "-"):
            slots[2] = plate
            display.lcd_display_string("Slot:B1", 1)
            available -= 1
            count += 1
            display.lcd_display_string(plate, 2)
            publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(plate) +'}', hostname="thingsboard.cloud", auth = {'username':"nXNiSJDI52nOQqiTy6F0", 'password':""})
        
        elif(slots[0] == "-" and slots[1] =="-"):
            num = r.randint(0,1)
            if(num == 0):
                slots[0] = plate
                display.lcd_display_string("Slot:A1", 1)
                publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(plate) +'}', hostname="thingsboard.cloud", auth = {'username':"4Zdi7c8BlbQB7nL1fLpq", 'password':""})
            else:
                slots[1] = plate
                display.lcd_display_string("Slot:A2", 1)
                publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(plate) +'}', hostname="thingsboard.cloud", auth = {'username':"yUYqesVqB0GBThmr1U4h", 'password':""})
            available -= 1
            count += 1
            display.lcd_display_string(plate, 2)
        
        elif(slots[0] == "-"):
            slots[0] = plate
            display.lcd_display_string("Slot:A1", 1)
            available -= 1
            count += 1
            display.lcd_display_string(plate, 2)
            publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(plate) +'}', hostname="thingsboard.cloud", auth = {'username':"4Zdi7c8BlbQB7nL1fLpq", 'password':""})
        
        elif(slots[1] == "-"):
            slots[1] = plate
            display.lcd_display_string("Slot:A2", 1)
            available -= 1
            count += 1
            display.lcd_display_string(plate, 2)
            publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(plate) +'}', hostname="thingsboard.cloud", auth = {'username':"yUYqesVqB0GBThmr1U4h", 'password':""})
        
        publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(available) +'}', hostname="thingsboard.cloud", auth = {'username':"l2W9Yt6qDEhBoTVj1FVB", 'password':""})
        publish.single(topic="v1/devices/me/telemetry", payload='{"value":' + str(count) +'}', hostname="thingsboard.cloud", auth = {'username':"xHyIFxSBeq87pbF3671m", 'password':""})
        print(str(count))
        arduino.write(b"1")
        time.sleep(3)
        arduino.write(b"2")
        time.sleep(1)
        display.lcd_clear()
        action = "0"
    display.lcd_display_string("Available:" + str(available), 1)
    if(count >= 2 and emailSend == False):
        server.sendmail('iotsmartparking2021@gmail.com', 'iotsmartparking2021@gmail.com',"Alert!!! Open Basement 2!!!")
        emailSend = True
        
    if(count < 2):
        emailSend = False
        
        

            
