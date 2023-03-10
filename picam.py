from picamera import PiCamera
from time import sleep
from datetime import datetime

camera = PiCamera()

date = "plant_" + datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
cameraInformation = "/home/pi/Desktop/" + date + ".png"

camera.start_preview()
sleep(5)
camera.capture(cameraInformation)
camera.stop_preview()

