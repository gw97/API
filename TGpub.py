# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 12:12:21 2018

@author: chris
"""

import time
from time import sleep
import datetime
import gspread
import logging
from oauth2client.service_account import ServiceAccountCredentials
from w1thermsensor import W1ThermSensor

logging.basicConfig(filename = 'app.log', level = logging.INFO)
#Sets a logging file for any exceptiosns raised by the code

def datareading():
#Temperature probe management, this will not break and manages any exceptions, if the incorrect
	data =[]
	for sensor in W1ThermSensor.get_available_sensors():
		data.append(sensor.get_temperature())
#For each available sensor the data from the sensor will be printed into the data list, this
#will cycle for as many sensors. The final insertion of the time ensures that the correct
#time corresponding to the final probe entering its data into the list is recorded
	return(data)

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
	Menu = input('Press b to begin log, press q to quit: ')
#Menu setup allowing the program to be run multiple times without turning the pi
#off
	now = datetime.datetime.now()
#Allows the backup file to be called todays date and time
	if Menu == 'b':
		f = str(inputno(1,'Please enter the test number: ',1,10))
		g = input('Enter Name: ')
#Test number allows the data writing to happen to the correct columns to stop
#overwriting. Beyond 10 and google sheets will raise an error due to the sheet
#being too long
		scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
		creds = ServiceAccountCredentials.from_json_keyfile_name('Client_temp.json', scope)
		client = gspread.authorize(creds)
		sheet = client.open("Temperature Data").sheet1
#Opens the correct sheet and correct tab, if the sheet is changed this needs
#changing
		sheet.update_cell(1,1+5*(int(f)-1),'Test Number: '+f)
		sheet.update_cell(1,2+5*(int(f)-1),g)
#Labels the data run with the number and specified name
		sheet.update_cell(2,1+5*(int(f)-1),'Time (s)')
		sheet.update_cell(2,2+5*(int(f)-1),'Temperature 1 (°C)')
		sheet.update_cell(2,3+5*(int(f)-1),'Temperature 2  (°C)')
		sheet.update_cell(2,4+5*(int(f)-1),'Temperature 3  (°C)')
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
				current_time = str(time.time() - start_time)
				Temperature_1,Temperature_2,Temperature_3 = datareading()
#Takes all readings, first checking if the VOC meter is functioning correctly
				try:
					sheet.update_cell(i,1+5*(int(f)-1), current_time)
					sheet.update_cell(i,2+5*(int(f)-1), Temperature_1)
					sheet.update_cell(i,3+5*(int(f)-1), Temperature_2)
					sheet.update_cell(i,4+5*(int(f)-1), Temperature_3)
#updates all the cells in turn
				except Exception as e:
					logging.error('Error occurred in sheet updating' + str(e))
#logs any error due to not connecting to google sheets correctly
					pass

				with open('Tempdata'+now.strftime("%Y-%m-%d %H-%M")+'.txt' ,'a+') as d:
					s =  str(current_time) + ',' + str(Temperature_1) + ',' + str(Temperature_2)+ ',' + str(Temperature_3)
					print (s)
					print (d, file=s)
#writes data to the backup datafile seperated by a comma

				if i % (5*6)/frequency == 0:
					try:
						scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
						creds = ServiceAccountCredentials.from_json_keyfile_name('Client_temp.json', scope)
						client = gspread.authorize(creds)
						sheet = client.open("Temperature Data").sheet1
						print('Authenticating.....')
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
