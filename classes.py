from gps3 import agps3
import time
import os
from datetime import datetime, timedelta
from pytz import timezone
import pytz

class MPU9250:
    def __init__(self):
        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        self.magnetic_direction = 0

    def get_pitch(self):
        return self.pitch

    def get_roll(self):
        return self.roll

    def get_yaw(self):
        return self.yaw

    def get_magenetic_direction(self):
        return self.magnetic_direction


class Thermometer:
    def __init__(self):
        self.temp = 0

    def get_temperature(self):
        return self.temp

class GPS:

    def __init__(self, metric=False):
        self.metric = metric
        self.speed = 0
        self.average_speed = 0
        self.average_count = 0
        self.distance_traveled = 0;
        self.start_time = time.monotonic()
        self.gps_socket = agps3.GPSDSocket()
        self.data_stream = agps3.DataStream()
        self.gps_socket.connect()
        self.gps_socket.watch()

    def update(self):
        while True:
            for new_data in self.gps_socket:
                if new_data:
                    self.data_stream.unpack(new_data)
                    self.speed = self.data_stream.speed
                    if (self.speed != "n/a"):
                        return True
            
        return False

    def get_speed(self):
        if self.metric:
            return self.speed
        else:
            return self.speed * 2.23694

    def get_average_speed(self, metric=None):
        if metric is None:
            metric = self.metric
        self.average_speed = ((self.average_speed * self.average_count) + self.speed) / (self.average_count + 1)
        self.average_count += 1
        if metric:
            return self.average_speed
        else:
            return self.average_speed * 2.23694

    def get_distance_traveled(self):
        self.distance_traveled = self.average_speed * (time.monotonic() - self.start_time)
        if self.metric:
            return self.distance_traveled
        else:
            return self.distance_traveled * .0006213712

    def get_time(self):
        return self.data_stream.time
    
    def update_time(self):
        t = self.get_time()
        split = t.split("-")
        year = split[0]
        month = split[1]
        day = split[2][:2]
        tim = t.split("T")[1][:8]
        
        gmt = pytz.timezone('GMT')
        eastern = pytz.timezone('US/Eastern')
        d = datetime.strptime(day + "/" + month + "/" + year + " " + tim + " GMT", '%d/%m/%Y %H:%M:%S GMT')
        dategmt = gmt.localize(d)
        dateeast = dategmt.astimezone(eastern)
        split = str(dateeast).split(" ")
        os.system("sudo date +%D -s " + split[0])
        os.system("sudo date +%T -s " + split[1][:-6])
        
        
    def i_dst(self, day, month, dow):
        if month < 3 or month > 11:
            return False
        elif month > 3 and month < 11:
            return True
        else:
            prev_sun = day - dow - 1
            if month == 3:
                return prev_sun >= 8
            else:
                return prev_sun <= 0
            


test = GPS()
test.update()
test.update_time()
while True:
    test.update()
    
    print (count)
    print("Time: ", test.get_time())
    print("Speed: %.2f" % test.get_speed())
    print("Average Speed: %.2f" % test.get_average_speed())
    print("Distance Traveled: %.2f" % test.get_distance_traveled())
    print()
    count += 1
    time.sleep(1)
