from gps3 import agps3
import time
import os
from datetime import datetime, timedelta
from pytz import timezone
import pytz

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
        """ Update data_stream and speed """
        while True:
            for new_data in self.gps_socket:
                if new_data:
                    self.data_stream.unpack(new_data)
                    self.speed = self.data_stream.speed
                    if (self.speed != "n/a"):
                        return

    def get_speed(self):
        """ Get speed

        Returns:
            speed (float) : in m/s or mph, depending on self.metric
        """
        if self.metric:
            return self.speed
        else:
            return self.speed * 2.23694

    def get_average_speed(self, metric=None):
        """ Get average_speed

        Args:
            metric (bool) : default=None, used to get distance_traveled

        Returns:
            average_speed (float) : in m/s or mph, depeding on metric
        """
        if metric is None:
            metric = self.metric
        self.average_speed = ((self.average_speed * self.average_count) + self.speed) / (self.average_count + 1)
        self.average_count += 1
        if metric:
            return self.average_speed
        else:
            return self.average_speed * 2.23694

    def get_distance_traveled(self):
        """ Get distance traveled

        Returns:
            distance (float) : in m or miles, depending on self.metric
        """
        self.distance_traveled = self.average_speed * (time.monotonic() - self.start_time)
        if self.metric:
            return self.distance_traveled
        else:
            return self.distance_traveled * .0006213712

    def get_time(self):
        """ Gets time

        Returns:
            time (str) : time and date
        """
        return self.data_stream.time

    def update_time(self):
        """ Sets system clock with time from gps """
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
