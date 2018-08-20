# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 15:52:36 2018

@author: chris
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 12:12:21 2018

@author: chris
"""

import time
from time import sleep
import datetime
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor

import gspread
from oauth2client.service_account import ServiceAccountCredentials


# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('Client_temp.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(17,GPIO.OUT)

def inputno(g, a, lim1, lim2):
#This defines the function used to check user inputs are within range and of correct data type
    if g == 1:
        while True:
            try:
                h = int(input(a))
                if lim1 <= h <= lim2:
                    return h
                else:
                    GPIO.output(17,GPIO.HIGH)
                    time.sleep(0.033)
                    GPIO.output(17,GPIO.LOW)
            except ValueError:
                GPIO.output(17,GPIO.HIGH)
                time.sleep(0.033)
                GPIO.output(17,GPIO.LOW)
                continue

def temperatures():
#Temperature probe management, this will not break and manages any exceptions, if the incorrect
    data =[]
    GPIO.output(18,GPIO.HIGH)
    for sensor in W1ThermSensor.get_available_sensors():
        data.append(sensor.get_temperature())
    GPIO.output(18,GPIO.LOW)
#For each available sensor the data from the sensor will be printed into the data list, this
#will cycle for as many sensors. The final insertion of the time ensures that the correct
#time corresponding to the final probe entering its data into the list is recorded
    return(data)


Menu = '0'
while Menu != 'q':
    Menu = input('Press b to begin log, press q to quit: ')
#Menu setup allowing the program to be run multiple times without turning the pi off
    now = datetime.datetime.now()
    if Menu == 'b':
        f = input('Please enter the test number: ')

        sheet = client.open("Temperature Data").sheet1
        sheet.update_cell(1,1+5*(int(f)-1),'Test Number: '+f)
        sheet.update_cell(2,1+5*(int(f)-1),'Time (s)')
        sheet.update_cell(2,2+5*(int(f)-1),'T1 (degrees)')
        sheet.update_cell(2,3+5*(int(f)-1),'T2 (degrees)')
        sheet.update_cell(2,4+5*(int(f)-1),'T3 (degrees)')
        
        frequency = inputno(1,'Period of data reading in seconds: ',1,100)
        length = int((inputno(1,'Run test for how many minutes: ',1,1500))*60/frequency)
        i = 3
        start_time = time.time()
        while(i < length+3):
            GPIO.output(18,GPIO.LOW)
            GPIO.output(17,GPIO.HIGH)
            t1 = time.time()
            t = str(time.time() - start_time) 
            z = temperatures()
            sheet.update_cell(i,1+5*(int(f)-1), t)
            sheet.update_cell(i,2+5*(int(f)-1), z[0])
            sheet.update_cell(i,3+5*(int(f)-1), z[1])
            sheet.update_cell(i,4+5*(int(f)-1), z[2])
                    
            with open('Temp'+now.strftime("%Y-%m-%d %H-%M")+'.txt' ,'a+') as d:
                s = t + ' ' + str(z[0]) + ' ' + str(z[1]) + ' ' + str(z[2])
                print(s)
                print(s,file=d)

            t2 = time.time()
            tT = t2-t1
            
            if frequency-tT <= 0:
                sleep(10)
            else:
                sleep(frequency-tT)
            i += 1
        d.close() 
        