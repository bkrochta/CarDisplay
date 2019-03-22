import time
import new
import math

sensor = new.MPU9250()
while True:
	"""
	print("Acceleration: ", sensor.readAccel())
	print("Gyroscope", sensor.readGyro())
	print("Magenetometer", sensor.readMagnet())
	print()
	"""
	
	dic = sensor.readMagnet()
	print((math.atan2(dic["y"],dic["x"])*180)/math.pi)
	time.sleep(.2)
