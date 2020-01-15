import obd
import time

class Car:

    def __init__ (self):
        self.speed = 0
        self.average_speed = 0
        self.average_count = 0
        self.distance_traveled = 0
        self.start_time = time.monotonic()

        def update_speed(self, r):
            self.speed = r.value

        self.connection = obd.Async()
        self.connection.watch(obd.commands.SPEED, callback=update_speed)
        self.connection.start()

    

    def get_speed(self):
        """ Get speed

        Returns:
            speed (float) : in mph
        """
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
        self.distance_traveled = self.average_speed * (time.monotonic() - self.start_time)
        
        return self.distance_traveled


