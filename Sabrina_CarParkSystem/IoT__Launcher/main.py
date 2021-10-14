import serial
import time
import random as r
import drivers
import cv2
import imutils
import time
import numpy as np
import pytesseract
from PIL import Image
from picamera.array import PiRGBArray
from picamera import PiCamera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))

device = '/dev/ttyUSB0'
arduino = serial.Serial(device, 9600)
display = drivers.Lcd()
action = "0"
count = 0
available = 2
slots = ["",""]
plate = ""

def capture():
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)
        key = action
        #if int(key) == 1:
        if key == ord("s"):
             gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #convert to grey scale
             gray = cv2.bilateralFilter(gray, 11, 17, 17) #Blur to reduce noise
             edged = cv2.Canny(gray, 30, 200) #Perform Edge detection
             cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE,              cv2.CHAIN_APPROX_SIMPLE)
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
        
    display.lcd_display_string("Available:" + str(available), 1)
    if(int(action) == 1):
        plate = capture()
        
        display.lcd_clear()
        if(slots[0] == plate):
            slots[0] = ""
            available += 1
            count -= 1
                
        elif(slots[1] == plate):
            slots[1] = ""
            available += 1
            count -= 1
             
        elif(slots[0] == "" and slots[1] ==""):
            num = r.randint(0,1)
            if(num == 0):
                slots[0] = plate
                display.lcd_display_string("Slot:A1", 1)
            else:
                slots[1] = plate
                display.lcd_display_string("Slot:A2", 1)
            available -= 1
            count += 1
            display.lcd_display_string(plate, 2)
        
        elif(slots[0] == ""):
            slots[0] = plate
            display.lcd_display_string("Slot:A1", 1)
            available -= 1
            count += 1
            display.lcd_display_string(plate, 2)
        
        elif(slots[1] == ""):
            slots[1] = plate
            display.lcd_display_string("Slot:A2", 1)
            available -= 1
            count += 1
            display.lcd_display_string(plate, 2)
        
        print(str(count))
        arduino.write(b"1")
        time.sleep(3)
        arduino.write(b"2")
        time.sleep(1)
        display.lcd_clear()
        action = "0"
        
        

            

