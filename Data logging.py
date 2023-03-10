import serial 
import time
import csv
from datetime import datetime

arduinoMeasurments = []

def logToCSV(temp,humidity,light,soilMoisture, waterLevel):
  log = open('/home/pi/Desktop/Moisture_test.csv', 'a')
  writer = csv.writer(log)
  sensorData = [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), temp, humidity, light, soilMoisture, waterLevel]
  writer.writerow(sensorData)
  log.close


if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout = 1)
    ser.reset_input_buffer()
    while True:
        ser.write(b"data\n")
        time.sleep(2)
        line = ser.readline().decode('utf-8').rstrip()
        print(line) 
        if line != '':
          arduinoMeasurments.append(line)
          print(arduinoMeasurments)
          time.sleep(1)
          if len(arduinoMeasurments) == 5:
            logToCSV(arduinoMeasurments[0], arduinoMeasurments[1],arduinoMeasurments[2],arduinoMeasurments[3],arduinoMeasurments[4])
            arduinoMeasurments = []
            time.sleep(600)    
