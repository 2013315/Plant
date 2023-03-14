import serial 
import csv
from datetime import datetime
import time
from time import sleep
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn import metrics
from picamera import PiCamera
from twilio.rest import Client
import PySimpleGUI as sg

maximumTemperature = [] 
averageHumidity = []
global watered
watered = 0 

global tolerance
tolerance = 440

sg.theme('DarkTeal')
sg.set_options(font=("Arial Bold", 14))


plantData = [[sg.Text(('Temperature: ' + '' + "C"), key='temp', text_color = 'white')], 
             [sg.Text(('Humidity: ' + '' + "%"), key='humidity', text_color = 'white')],
             [sg.Text(('Soil moisture: ' + '' + "%"), key='moisture',text_color = 'white')],
             [sg.Text(('Water Level: ' + '' + "cm"), key='waterLevel',text_color = 'white')],
]

phone1 = sg.Text('Please enter your phone number: ', font=('Arial Bold', 15), key='-OUT-', expand_x = True, text_color = 'white')
phone2 = sg.Input('', enable_events=True, key='-INPUT-', expand_x=False, font=('Arial Bold', 15), text_color='white')
Enter = sg.Button('Enter', key='-Enter-', font=('Arial Bold', 15))

plant1 = sg.Text('Enter your plant name: ', font=('Arial Bold', 15), key='-OUT-', expand_x = True, text_color = 'white')
plant2 = sg.Input('', enable_events=True, key='-INPUT-', expand_x=False, font=('Arial Bold', 15), text_color='white')
name = sg.Button('Name!', key='-name-', font=('Arial Bold', 15))

plantframe = sg.Frame('Plant Data', plantData,)

image = [sg.Image('/home/pi/Desktop/plant_2023-03-09_12:24:25.png', key='photo')]



columnLayout = [[sg.Column([[plantframe]], justification='centre'), sg.VSeperator(), sg.Column([image])],
        [plant1], [plant2], [name],
        [phone1], [phone2], [Enter]]

layout = [[sg.Column(columnLayout, scrollable=True, vertical_scroll_only=True, expand_x=True)]]

window = sg.Window("Plant Data", layout, resizable=True)

event, values = window.read(timeout = 10)

def sendText(bod, phoneNumber):
  account_sid = "account_sid"
  auth_token = "auth_token"

  client = Client(account_sid, auth_token)

  target = "+61" + phoneNumber

  message = client.api.account.messages.create(

  to= target,

  from_="+twilio_phone_number",

  body= bod) 


def getTime():
  #convert current time into something that can be used by the regression model
  midnight = datetime.strptime("00:00:00", '%H:%M:%S')
  currentTime = datetime.now().strftime('%H:%M:%S')
  currentTime = datetime.strptime(currentTime, '%H:%M:%S')
  difference = currentTime - midnight
  timeSeconds = difference.total_seconds()
  return timeSeconds

def takePhoto():
  camera = PiCamera()

  date = "plant_" + datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
  cameraInformation = "/home/pi/Desktop/" + date + ".png"

  camera.resolution = (800, 600)

  camera.start_preview()
  sleep(5)
  camera.capture(cameraInformation)
  camera.stop_preview()
  window["photo"].update(cameraInformation)

def updateGUI(arduinoMeasurements):
  window["temp"].update("Temperature: "+str(arduinoMeasurements[0])+"C")
  window["humidity"].update("Humidity: "+str(arduinoMeasurements[1])+"%")
  #assuming that moisture has a minimum of 400 and a max of 800
  #calculate percentage of soil moisture
  moisture = ((int(arduinoMeasurements[3])-400)/400)*100
  window["moisture"].update("Moisture: "+str(moisture)+"%")
  window["waterLevel"].update("Water level: "+str(arduinoMeasurements[4])+"cm")


def regression(tolerance):
  #choose random forest regression
  regressor = RandomForestRegressor(n_estimators=1, random_state=0)

  #load the file using pandas
  sensorData = ("Date", "Time", "Temperature", "Humidity", "Light", "Soil_Moisture", "Water_Level")

  df = pd.read_csv("/home/pi/Desktop/regressionTest.csv", names=sensorData)

  #get last 50 values
  df = df.tail(50)

  #predict moisture based off time

  tempX = df['Time']
  tempY = df['Soil_Moisture']

  tempX = tempX.values.reshape(-1, 1)
  tempY = tempY.values.ravel()

  #split values into train and test to adjust the model 

  Xtrain, Xtest, Ytrain, Ytest = train_test_split(tempX, tempY, test_size= 0.25, random_state=0)

  regressor.fit(Xtrain, Ytrain)
  prediction = regressor.predict(Xtest)

  #use error calculations to test model
  absoluteError = metrics.mean_absolute_error(Ytest, prediction)
  squaredError = metrics.mean_squared_error(Ytest, prediction)
  bestEstimator = 1

  ##get start time
  startTime = datetime.now().strftime('%H:%M:%S')
  print("Start time:", startTime)
  startTime = datetime.strptime(startTime, '%H:%M:%S')

  #find the best N_estimator 
  for b in range(1,100):
    regressor = RandomForestRegressor(n_estimators=b, random_state=0)
    Xtrain, Xtest, Ytrain, Ytest = train_test_split(tempX, tempY, test_size= 0.25, random_state=0)
    regressor.fit(Xtrain, Ytrain)
    prediction = regressor.predict(Xtest)
    if (absoluteError > metrics.mean_absolute_error(Ytest, prediction)) and (squaredError > metrics.mean_squared_error(Ytest, prediction)):
        absoluteError = metrics.mean_absolute_error(Ytest, prediction)
        squaredError = metrics.mean_squared_error(Ytest, prediction)
        bestEstimator = b 

  endTime = datetime.now().strftime('%H:%M:%S')
  print("End time:", endTime)
  endTime = datetime.strptime(endTime, '%H:%M:%S')

  #print runtime
  runTime = (endTime - startTime).total_seconds()
  print("The program ran in", runTime, "s and searched 100 n_estimators")

  print("Absolute error:", absoluteError)
  print("Squared error:", squaredError)
  print("Best n_estimator:", bestEstimator)
  regressor = RandomForestRegressor(n_estimators= bestEstimator, random_state=0)

  #fit model to values
  regressor.fit(tempX, tempY)

  currentTime = int(getTime())

  #calculate when the soil will dry based on regression model
  for x in range(currentTime, 86400, 30):
    guess = int(regressor.predict([[x]]))
    if guess > (tolerance-30) and guess < (tolerance+30):
      break
    
  print("Time:", x)
  print("Moisture:", guess)

  return x, regressor


def logToCSV(temp,humidity,light,soilMoisture, waterLevel):
  log = open('/home/pi/Desktop/regressionTest.csv', 'a')
  writer = csv.writer(log)
  
  timeSeconds = getTime()
  sensorData = [datetime.now().strftime('%Y-%m-%d'), timeSeconds, temp, humidity, light, soilMoisture, waterLevel]
  writer.writerow(sensorData)
  log.close

def getMeasurements ():
  arduinoMeasurements = []
  if __name__ == '__main__':
      ser = serial.Serial('/dev/ttyACM0', 9600, timeout = 1)
      ser.reset_input_buffer()
      while True:
        ser.write(b"data\n")
        line = ser.readline().decode('utf-8').rstrip()
        print(line) 
        if line != '':
          arduinoMeasurements.append(line)
          print(arduinoMeasurements)
          if len(arduinoMeasurements) == 5:
            logToCSV(arduinoMeasurements[0], arduinoMeasurements[1],arduinoMeasurements[2],arduinoMeasurements[3],arduinoMeasurements[4])
            updateGUI(arduinoMeasurements)
            return arduinoMeasurements

def pump():
  if __name__ == '__main__':
      ser = serial.Serial('/dev/ttyACM0', 9600, timeout = 1)
      ser.reset_input_buffer()
      while True:
        ser.write(b"pump\n")
        line = ser.readline().decode('utf-8').rstrip()
        if line == "received":
          break
      while True:
        line = ser.readline().decode('utf-8').rstrip()
        print(line) 
        if line == "completed":
          break

global number
number = ''

timeUntilDry = 0

while True: 
  if event == sg.WIN_CLOSED:
    break
  if event == '-Enter-':
    if (values['-INPUT-1']).isdigit() == False:
      sg.popup("Please enter only digits.")
      window['-INPUT-1'].update(values['-INPUT-'])
    else:
      number = str(values['-INPUT-1'])
      print(number)
      sg.popup("Phone number successfully registered!")
      window['-INPUT-1'].update(values['-INPUT-1'][:-100])
  if event == '-name-':
    name = str(values['-INPUT-'])
    sg.popup("Congratulations! You named your plant:", name)
    window['-INPUT-'].update(values['-INPUT-'][:-100])
  event, values = window.read(timeout = 10)

  if event == sg.TIMEOUT_KEY:
    timeSeconds = getTime()
      
    #check if morning to water plant
    if timeSeconds >27600 and timeSeconds < 27605:
      #take a daily picture of the plant
    
      takePhoto()
    
      #reset average humidity, number of times watered and temp at the start of the day
      maximumTemperature = [] 
      averageHumidity = [] 
      watered = 0 
      #get measurements and check if water moisture is below certain value
      arduinoMeasurements = getMeasurements()
      if int(arduinoMeasurements[3]) < tolerance:
        #water moisture is too low 
        pump()
        watered += 1
      #get data for regression prediction 
      for x in range (0,50):
        getMeasurements()
        sleep(30)
      timeUntilDry, regressor = regression(tolerance)


    #check if the water is be dry at this point 
    if timeUntilDry == timeSeconds and timeSeconds > 28800 and timeSeconds < 64800:
      arduinoMeasurements = getMeasurements()
      # don't water late in the afternoon (1800) 
      if int(arduinoMeasurements[3]) < tolerance:
        #water moisture is too low 
        pump()
        watered += 1
        #get data for regression prediction
        for x in range (0,50):
          getMeasurements()
          sleep(30)
        timeUntilDry, regressor = regression(tolerance)

    #log data every 30 min
    if timeSeconds%1800==0:
      arduinoMeasurements = getMeasurements()
      maximumTemperature.append(arduinoMeasurements[0])
      averageHumidity.append(arduinoMeasurements[1])
    
      #check the accuracy of the prediction every 2 hours between 0800 and 1800
  
      if timeSeconds%7200==0 and timeSeconds > 28800 and timeSeconds < 64800:
        #get values to calculate percentage error
        predicted = int(regressor.predict([[timeSeconds]]))
        measured = arduinoMeasurements[3] 
        percentageError = ((abs(predicted-measured))/measured)*100
        #if error is too high recalculate regression
        print(percentageError)
        if percentageError > 30: 
          for x in range (0,50):
            getMeasurements()
            sleep(30)
          timeUntilDry, regressor = regression(tolerance)
    
    #at 1826 send text 

    if timeSeconds > 66360 and timeSeconds < 66540 and number != '':

      maximumTemperature.sort()
      maxtemp = maximumTemperature[-1]
      avHumidity = sum(averageHumidity)/len(averageHumidity)
      
      message = "Hi, " + name + " experienced a maximum temperature of " + str(maxtemp) + "C with an average humidity of " + str(avHumidity) + "%. " + name + " was watered: " + str(watered) + " times."
      #add message to fill up water 
      #f arduinoMeasurements[4] > 10:
        message += " Warning your water supply is low!"
      sendText(message, number)

      while timeSeconds < 66540:
        timeSeconds = getTime()
