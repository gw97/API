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
#Sets a logging file for any exceptiosns raised by the code

ccs =  Adafruit_CCS811()
while not ccs.available():
	pass
temp = ccs.calculateTemperature()
ccs.tempOffset = temp - 25.0
#Initializes the VOC meter using the Adafruit library. Calculate temperature is
#an object function and is caclulated not measured so inaccurate.

#Scope gives the correct authority to the code so that it can access the correct
#APIs, this does not need changing. Creds are the credentials, taken from the
#.json file which needs to be in the same working directory as this python file

def datareading():
	current_time = str(time.time() - start_time)
	VOCs = str(ccs.getTVOC())
	CO2 = str(ccs.geteCO2())
#T calculates the current time in seconds of the program when the reading is
#taken. x and y are both variables assigned to the VOC and CO2 values taken
#from the voc meter.
	return (current_time,VOCs,CO2)

def inputno(input_type,input_text, lim1, lim2):
#This defines the function used to check user inputs are within range and of correct data type
	if input_type == 1:
		while True:
			try:
				h = int(input(input_text))
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
#Menu setup allowing the program to be run multiple times without turning the pi
#off
	now = datetime.datetime.now()
#Allows the backup file to be called todays date and time
	if Menu == 'b':
		f = str(inputno(1,'Please enter the test number: ',1,10))
		g = raw_input('Enter Name: ')
#Test number allows the data writing to happen to the correct columns to stop
#overwriting. Beyond 10 and google sheets will raise an error due to the sheet
#being too long
		scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
		creds = ServiceAccountCredentials.from_json_keyfile_name('Client_secret.json', scope)
		client = gspread.authorize(creds)
		sheet = client.open("VOC Data").sheet1
#Opens the correct sheet and correct tab, if the sheet is changed this needs
#changing
		sheet.update_cell(1,1+5*(int(f)-1),'Test Number: '+f)
		sheet.update_cell(1,2+5*(int(f)-1),g)
#Labels the data run with the number and specified name
		sheet.update_cell(2,1+5*(int(f)-1),'Time (s)')
		sheet.update_cell(2,2+5*(int(f)-1),'VOCs (ppb)')
		sheet.update_cell(2,3+5*(int(f)-1),'eCO2 (ppm)')
		sheet.update_cell(2,4+5*(int(f)-1),'Chip Temp (°C)')
#Names the columns with the correct headings and units.
		frequency = inputno(1,'Period of data reading in seconds: ',1,100)
		length = int((inputno(1,'Run test for how many minutes: ',1,1500))*60/frequency)
#Inputs the correct period of logging and how long the test is converted into
#a number of readings to be taken
		i = 3
		start_time = time.time()
#i is initialized as 3 to prevent the column headings being overwritten
		while(i < length+3):
#Total main loop in which all readings occur
			try:
				t1 = time.time()
				if ccs.available():
					temp = str(ccs.calculateTemperature())
					if not ccs.readData():
						current_time,VOC,CO2 = datareading()
#Takes all readings, first checking if the VOC meter is functioning correctly
						try:
							sheet.update_cell(i,1+5*(int(f)-1), current_time)
							sheet.update_cell(i,2+5*(int(f)-1), VOC)
							sheet.update_cell(i,3+5*(int(f)-1), CO2)
							sheet.update_cell(i,4+5*(int(f)-1), temp)
#updates all the cells in turn
						except Exception as e:
							logging.error('Error occurred in sheet updating' + str(e))
#logs any error due to not connecting to google sheets correctly
							pass

						with open('VOCdata'+now.strftime("%Y-%m-%d %H-%M")+'.txt' ,'a+') as d:
							s =  str(current_time) + ',' + str(VOC) + ',' + str(CO2)+ ',' + temp
							print s
							print >>d, s
#writes data to the backup datafile seperated by a comma
					else:
						while(1):
							pass
#If the VOC meter is unavailable, wait
				if i % (5*6)/frequency == 0:
					try:
						scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
						creds = ServiceAccountCredentials.from_json_keyfile_name('Client_secret.json', scope)
						client = gspread.authorize(creds)
						sheet = client.open("VOC Data").sheet1
#reauthenticates the code so that google does not block the sheet request
					except Exception as e:
						logging.error('Error occurred in authentication' + str(e))
#If this fails, log the error
						pass

				t2 = time.time()
				if frequency-(t2-t1) <= 0:
					sleep(10)
#Calculates how long the taking of data and writing to google and ensures the
#frequency of readings doesn't drift. If less than 0 will check the reading
#didn't take longer than the period
				else:
					sleep(frequency-(t2-t1))
				i += 1

			except Exception as e:
				logging.error('Error occurred in full code' + str(e))
				print 'err',i
#Any extra error will be caught by this logging system, and will rerun the
#content of the while loop
				sleep(10)
				i += 1
		d.close()
	if Menu == 'q':
		exit()
