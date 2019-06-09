import os
import time

class Thermometer:


    def __init__(self, address):
        os.system('modprobe w1-gpio') # turn on GPIO module
        os.system('modprobe w1-therm') # turn on temperature module
        self.device_file = '/sys/bus/w1/devices/' + address + '/w1_slave'


    def get_temp(self):
        """ Get temp data from sensor

        Returns:
            temp_f (int) : temperature in fahrenheit
        """
        while True:
            try:
                with open(self.device_file, 'r') as f:
                    lines = f.readlines()   # raw temperature data
                    if lines[0].strip()[-3:] == 'YES':  # check if ready
                        break

            except IOError as e:
                print("Failed opening device_file")
                time.sleep(5)
                return None
        equal_pos = lines[1].find('t=') # find temperature in file
        if equal_pos != -1:
            temp_string = lines[1][equal_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return int(temp_f)
        return None
