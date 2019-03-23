import mpu9250
import gps


class Thermometer:
    def __init__(self):
        self.temp = 0

    def get_temperature(self):
        return self.temp



# testgps = gps.GPS()
# testgps.update()
# testgps.update_time()
# while True:
#     testgps.update()
#
#     print (count)
#     print("Time: ", testgps.get_time())
#     print("Speed: %.2f" % testgps.get_speed())
#     print("Average Speed: %.2f" % testgps.get_average_speed())
#     print("Distance Traveled: %.2f" % testgps.get_distance_traveled())
#     print()
#     count += 1
#     time.sleep(1)

test = mpu9250.MPU9250()
test.calibrate()


while True:
    print("Accel ", test.readAccel())
    print("Gyro ", test.readGyro())
    mag = test.read()
    print("Magnet ", mag)
    dir = math.atan2(mag[1],mag[0])*(180/math.pi)
    print(dir)
    print(test.get_heading(dir))
    print()
    time.sleep(.5)
