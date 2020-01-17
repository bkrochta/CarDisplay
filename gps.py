from gps3.agps3threaded import AGPS3mechanism
import time
import os
from datetime import datetime, timedelta
from pytz import timezone
import pytz


class GPS:
    def __init__(self, metric=False):
        self.gps_thread = AGPS3mechanism()
        self.gps_thread.stream_data()
        self.gps_thread.run_thread()

    def get_heading(self):
        heading = self.gps_thread.data_stream.track

        if heading < 0:
            heading += 360
        if heading == 0.0 or heading == 'n/a':
            return None
        if(heading <= 22.5):
            return "N"
        elif(heading < 67.5):
            return "NE"
        elif(heading <= 112.5):
            return "E"
        elif(heading < 157.5):
            return "SE"
        elif(heading <= 202.5):
            return "S"
        elif(heading < 247.5):
            return "SW"
        elif(heading <= 292.5):
            return "W"
        elif(heading < 337.5):
            return "NW"
        else:
            return "N"

    def update_time(self):
        print("start")
        """ Sets system clock with time from gps """
        while True:
            t = self.gps_thread.data_stream.time
            if t != 'n/a':
                break
            time.sleep(.1)
        split = t.split("-")
        year = split[0]
        month = split[1]
        day = split[2][:2]
        tim = t.split("T")[1][:8].split(':')

        utc = pytz.utc
        eastern = pytz.timezone('US/Eastern')
        d = datetime(int(year), int(month), int(day), int(tim[0]), int(tim[1]), int(tim[2]), tzinfo=utc)
        dateeast = d.astimezone(eastern)
        split = str(dateeast).split(" ")
        os.system("sudo date +%D -s " + split[0])
        os.system("sudo date +%T -s " + split[1][:-6])
        print("done")
