import obd
import time
import os
import time

class Car:

    def __init__ (self, address):
        os.system('sudo rfcomm bind 0 ' + address)
        time.sleep(1)
        self.speed = 0
        self.average_speed = 0
        self.average_count = 0
        self.distance_traveled = 0
        self.start_time = time.monotonic()
        #obd.logger.setLevel(obd.logging.DEBUG)
        self.connection = obd.OBD()
    

    def get_speed(self):
        """ Get speed

        Returns:
            speed (float) : in mph
        """
        self.speed = self.connection.query(obd.commands.SPEED).value.to('mph').magnitude

        return self.speed


    def get_average_speed(self):
        """ Get average_speed

        Returns:
            average_speed (float) : in mph
        """
        self.average_speed = ((self.average_speed * self.average_count) + self.speed) / (self.average_count + 1)
        self.average_count += 1
        
        return self.average_speed


    def get_distance_traveled(self):
        """ Get distance traveled

        Returns:
            distance (float) : in miles
        """
        self.distance_traveled = self.average_speed * (time.monotonic() - self.start_time) / 3600
        
        return self.distance_traveled


