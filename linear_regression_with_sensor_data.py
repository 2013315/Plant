import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.linear_model import LinearRegression

sensorData = ("Date", "Time", "Temperature", "Humidity", "Light", "Soil_Moisture", "Water_Level")

df = pd.read_csv("/home/pi/Desktop/regressionTest.csv", names=sensorData)

df = df.head(20)

##Final prediction 

x= df[["Temperature", "Humidity", "Light", "Soil_Moisture"]]
y = df["Time"]

regr = linear_model.LinearRegression()
regr.fit(x.values,y)

##temp prediction

tempX = df['Time']
tempY = df['Temperature']

tempX = tempX.values.reshape(-1, 1)
tempY = tempY.values.reshape(-1, 1)

regrTemp = linear_model.LinearRegression()

regrTemp.fit(tempX, tempY)

##humidity prediction

humidityX = df['Time']
humidityY = df['Humidity']

humidityX = humidityX.values.reshape(-1, 1)
humidityY = humidityY.values.reshape(-1, 1)

regrHumidity = linear_model.LinearRegression()

regrHumidity.fit(humidityX, humidityY)

##light prediction

lightX = df['Time']
lightY = df['Light']

lightX = lightX.values.reshape(-1, 1)
lightY = lightY.values.reshape(-1, 1)

regrLight = linear_model.LinearRegression()

regrLight.fit(lightX, lightY)

##inital time prediction using average of measured values
avTemp = sum(df.loc[0:19,"Temperature"])/20
avHumidity = sum(df.loc[0:19,"Humidity"])/20
avLight = sum(df.loc[0:19,"Light"])/20

predictedTime = int(regr.predict([[avTemp, avHumidity, avLight, 777]])) ##soil moisture remains constant as this the value that needs to be predicted
for b in range (0, 15):
    predictedTemp = int(regrTemp.predict(np.array([predictedTime]).reshape(1,1)))
    predictedLight = int(regrHumidity.predict(np.array([predictedTime]).reshape(1,1)))
    predictedHumidity = int(regrHumidity.predict(np.array([predictedTime]).reshape(1,1)))
    predictedTime = int(regr.predict([[predictedTemp, predictedHumidity, predictedLight, 777]]))

plt.scatter(humidityX, humidityY)
plt.ylabel("humidity")
plt.xlabel("time")
plt.title("Humidity")
plt.plot(humidityX, regrHumidity.predict(humidityX), color="red")
plt.draw()
plt.pause(20)
plt.close()

plt.scatter(tempX, tempY)
plt.ylabel("temp")
plt.xlabel("time")
plt.title("temp")
plt.plot(tempX, regrTemp.predict(tempX), color="red")
plt.draw()
plt.pause(20)
plt.close()

plt.scatter(lightX, lightY)
plt.ylabel("light")
plt.xlabel("time")
plt.title("light")
plt.plot(lightX, regrLight.predict(lightX), color="red")
plt.draw()
plt.pause(20)
plt.close()

print("Predicted light:", predictedLight)
print("Predicted humidity:", predictedHumidity)
print("predicted temp:", predictedTemp)
print("Predicted time:", predictedTime)