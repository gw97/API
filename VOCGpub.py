# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 12:12:21 2018

@author: chris
"""

import time
from time import sleep
from Adafruit_CCS811 import Adafruit_CCS811
import datetime
import gspread
import logging
from oauth2client.service_account import ServiceAccountCredentials

logging.basicConfig(filename = 'app.log', level = logging.INFO)

ccs =  Adafruit_CCS811()
while not ccs.available():
	pass
temp = ccs.calculateTemperature()
ccs.tempOffset = temp - 25.0

def authenticate():
	scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
	creds = ServiceAccountCredentials.from_json_keyfile_name('Client_secret.json', scope)
	client = gspread.authorize(creds)

def datareading():
	t = str(time.time() - start_time)
	x = str(ccs.getTVOC())
	y = str(ccs.geteCO2())
	return (t,x,y)

def inputno(g, a, lim1, lim2):
#This defines the function used to check user inputs are within range and of correct data type
    if g == 1:
        while True:
            try:
                h = int(input(a))
                if lim1 <= h <= lim2:
                    return h
                else:
                    time.sleep(0.033)
            except ValueError:
                time.sleep(0.033)
                continue
Menu = '0'
while Menu != 'q':
    Menu = raw_input('Press b to begin log, press q to quit: ')
#Menu setup allowing the program to be run multiple times without turning the pi off
    now = datetime.datetime.now()
    if Menu == 'b':
        f = raw_input('Please enter the test number: ')
        g = raw_input('Enter Name: ')

        sheet = client.open("VOC Data").sheet1
        sheet.update_cell(1,1+5*(int(f)-1),'Test Number: '+f)
        sheet.update_cell(1,2+5*(int(f)-1),g)
        sheet.update_cell(2,1+5*(int(f)-1),'Time (s)')
        sheet.update_cell(2,2+5*(int(f)-1),'VOCs (ppb)')
        sheet.update_cell(2,3+5*(int(f)-1),'eCO2 (ppm)')
        sheet.update_cell(2,4+5*(int(f)-1),'Chip Temp (degrees)')

        frequency = inputno(1,'Period of data reading in seconds: ',1,100)
        length = int((inputno(1,'Run test for how many minutes: ',1,1500))*60/frequency)
        i = 3
        start_time = time.time()

        while(i < length+3):
            try:
                t1 = time.time()
                if ccs.available():
                    temp = str(ccs.calculateTemperature())
                    if not ccs.readData():
						time,VOC,CO2 = datareading()
						try:
	                        sheet.update_cell(i,1+5*(int(f)-1), time)
	                        sheet.update_cell(i,2+5*(int(f)-1), VOC)
	                        sheet.update_cell(i,3+5*(int(f)-1), CO2)
	                        sheet.update_cell(i,4+5*(int(f)-1), temp)
						except Exception as e:
							logging.error('Error occurred in sheet updating' + str(e))
							pass

                        with open('VOCdata'+now.strftime("%Y-%m-%d %H-%M")+'.txt' ,'a+') as d:
                            s =  str(time) + ' ' + str(VOC) + ' ' + str(CO2)+ ' ' + temp
                            print s
                            print >>d, s
                    else:
                        while(1):
                            pass

				if i % (5*6)/frequency == 0:
					try:
		            	authenticate()
		            	sheet = client.open("VOC Data").sheet1
					except Exception as e:
						logging.error('Error occurred in authentication' + str(e))
						pass

                t2 = time.time()
                if frequency-(t2-t1) <= 0:
                    sleep(10)
                else:
                    sleep(frequency-(t2-t1))
                i += 1

            except Exception as e:
				logging.error('Error occurred in full code' + str(e))
                print 'err',i
				sleep(10)
        d.close()
