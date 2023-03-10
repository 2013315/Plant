from time import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn import metrics
from datetime import datetime

regressor = RandomForestRegressor(n_estimators=1, random_state=0)

sensorData = ("Date", "Time", "Temperature", "Humidity", "Light", "Soil_Moisture", "Water_Level")

df = pd.read_csv("/home/pi/Desktop/regressionTest.csv", names=sensorData)

df = df.tail(50)

##temp prediction

tempX = df['Time']
tempY = df['Soil_Moisture']

tempX = tempX.values.reshape(-1, 1)
tempY = tempY.values.ravel()

Xtrain, Xtest, Ytrain, Ytest = train_test_split(tempX, tempY, test_size= 0.25, random_state=0)

regressor.fit(Xtrain, Ytrain)
prediction = regressor.predict(Xtest)

absoluteError = metrics.mean_absolute_error(Ytest, prediction)
squaredError = metrics.mean_squared_error(Ytest, prediction)
bestEstimator = 1

##get start time
startTime = datetime.now().strftime('%H:%M:%S')
print("Start time:", startTime)
startTime = datetime.strptime(startTime, '%H:%M:%S')

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

runTime = (endTime - startTime).total_seconds()
print("The program ran in", runTime, "s and searched 100 n_estimators")

print("Absolute error:", absoluteError)
print("Squared error:", squaredError)
print("Best n_estimator:", bestEstimator)
regressor = RandomForestRegressor(n_estimators= bestEstimator, random_state=0)

regressor.fit(tempX, tempY)

currentTime = datetime.now().strftime('%H:%M:%S')
currentTime = datetime.strptime(currentTime, '%H:%M:%S')

currentTime = 32400
for x in range(currentTime, 86400, 30):
  guess = int(regressor.predict([[x]]))
  if guess > 730 and guess < 810:
      break
    
print("Time:", x)
print("Moisture:", guess)

plt.scatter(tempX, tempY)
plt.ylabel("Moisture level (%)")
plt.xlabel("Time (s since midnight)")
plt.title("Moisture levels over time")
plt.plot(tempX, regressor.predict(tempX), color="red")
plt.draw()
plt.pause(30)
plt.close('all')
