import os
import time

class Thermometer:
    def __init__(self, address):
        os.system('modprobe w1-gpio') # turn on GPIO module
        os.system('modprobe w1-therm') # turn on temperature module
        self.device_file = '/sys/bus/w1/devices/' + address + '/w1/slave'

    def read_temp_raw(self):
        """ Get raw temp data from sensor

        Returns:
            lines (str) : temperature data
        """
        try:
            with open(self.device_file, 'r') as f:
                lines = f.readlines()
                return lines
        except IOError as e:
            print("Failed opening device_file")
            return None

    def read_temp(self):
        """ Converts raw temp data to fahrenheit

        Returns:
            temp (float) : temperature in fahrenheit
        """
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(.2)
            lines = self.read_temp_raw()
        equal_pos = lines[1].find('t=')
        if equal_pos != -1:
            temp_string = lines[1][equal_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_f
