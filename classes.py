from gps3 import agsp3
import time

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

    def __init__(self):
        self.speed = 0
        self.average_speed = 0
        self.average_count = 1
        self.distance_traveled = 0;
        self.start_time = time.monotonic()
        self.gps_socket = agps3.GPSDSocket()
        self.data_stream = agps3.DataStream()
        self.gps_socket.connect()
        self.gps_socket.watch()

    def update(self):
        for new_data in gps_socket:
            if new_data:
                data_stream.unpack(new_data)
                self.speed = data_stream.speed

    def get_speed(self):
        self.speed = self.data_stream.speed
        return self.speed

    def get_average_speed(self):
        self.average_speed = ((self.average_speed * self.average_count) + get_speed()) / (self.average_count + 1)
        self.average_count++
        return self.average_speed

    def get_distance_traveled(self):
        self.distance_traveled = get_average_speed() * (time.monotonic - self.start_time)
        return self.distance_traveled

    def get_time(self):
        return self.data_stream.time

test = mpu9250()
print(test.get_roll())
