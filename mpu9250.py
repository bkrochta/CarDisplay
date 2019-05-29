import smbus
import time
import numpy as np
import math
from scipy import linalg
import pickle

### https://www.invensense.com/wp-content/uploads/2015/02/RM-MPU-9250A-00-v1.6.pdf
## MPU9250 Default I2C slave address
SLAVE_ADDRESS        = 0x68
## AK8963 I2C slave address
AK8963_SLAVE_ADDRESS = 0x0C
## Device id
DEVICE_ID            = 0x71

''' MPU-9250 Register Addresses '''
## sample rate driver
SMPLRT_DIV     = 0x19
CONFIG         = 0x1A
GYRO_CONFIG    = 0x1B
ACCEL_CONFIG   = 0x1C
ACCEL_CONFIG_2 = 0x1D
LP_ACCEL_ODR   = 0x1E
WOM_THR        = 0x1F
FIFO_EN        = 0x23
I2C_MST_CTRL   = 0x24
I2C_MST_STATUS = 0x36
INT_PIN_CFG    = 0x37
INT_ENABLE     = 0x38
INT_STATUS     = 0x3A
ACCEL_OUT      = 0x3B
TEMP_OUT       = 0x41
GYRO_OUT       = 0x43

I2C_MST_DELAY_CTRL = 0x67
SIGNAL_PATH_RESET  = 0x68
MOT_DETECT_CTRL    = 0x69
USER_CTRL          = 0x6A
PWR_MGMT_1         = 0x6B
PWR_MGMT_2         = 0x6C
FIFO_R_W           = 0x74
WHO_AM_I           = 0x75

## Gyro Full Scale Select 250dps
GFS_250  = 0x00
## Gyro Full Scale Select 500dps
GFS_500  = 0x01
## Gyro Full Scale Select 1000dps
GFS_1000 = 0x02
## Gyro Full Scale Select 2000dps
GFS_2000 = 0x03
## Accel Full Scale Select 2G
AFS_2G   = 0x00
## Accel Full Scale Select 4G
AFS_4G   = 0x01
## Accel Full Scale Select 8G
AFS_8G   = 0x02
## Accel Full Scale Select 16G
AFS_16G  = 0x03

# AK8963 Register Addresses
AK8963_ST1        = 0x02 # data ready register
AK8963_MAGNET_OUT = 0x03
AK8963_CNTL1      = 0x0A
AK8963_CNTL2      = 0x0B
AK8963_ASAX       = 0x10

# CNTL1 Mode select
## Power down mode
AK8963_MODE_DOWN   = 0x00
## One shot data output
AK8963_MODE_ONE    = 0x01

## Continous data output 8Hz
AK8963_MODE_C8HZ   = 0x02
## Continous data output 100Hz
AK8963_MODE_C100HZ = 0x06

# Magneto Scale Select
## 14bit output
AK8963_BIT_14 = 0x00
## 16bit output
AK8963_BIT_16 = 0x01

class MPU9250:
    ## Constructor
    #  @param [in] address MPU-9250 I2C slave address default:0x68
    def __init__(self, calibrate=False, address=SLAVE_ADDRESS,):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.config(GFS_250, AFS_2G, AK8963_BIT_16, AK8963_MODE_C8HZ)

        # initialize values
        self.max_x = -100000
        self.max_y = -100000
        self.max_z = -100000
        self.min_x = 100000
        self.min_y = 100000
        self.min_z = 100000

        self.x_hist = []
        self.y_hist = []
        self.z_hist = []

        self.F   = 1
        if not calibrate:
            try:
                self.b = np.load('b.npy')
                self.A_1 = np.load('a.npy')
            except IOError as e:
                print("No calibration data")
                self.b   = np.zeros([3, 1])
                self.A_1 = np.eye(3)
        else:
            self.b   = np.zeros([3, 1])
            self.A_1 = np.eye(3)

    def config(self, gfs, afs, mfs, mode):
        """ Configure MPU9250 and AK8963

        Args:
            gfd (hex): Gyroscope Full Scale Select(default:GFS_250[+250dps])
            afs (hex): Accelerometer Full Scale Select(default:AFS_2G[2g])
            mfs (hex) : Magneto Scale Select(default:AK8963_BIT_16[16bit])
            mode (hex) : Magenetometer mode select(default:AK8963_MODE_C8HZ[Continous 8Hz])

        """
        if gfs == GFS_250:
            self.gres = 250.0/32768.0
        elif gfs == GFS_500:
            self.gres = 500.0/32768.0
        elif gfs == GFS_1000:
            self.gres = 1000.0/32768.0
        else:  # gfs == GFS_2000
            self.gres = 2000.0/32768.0

        if afs == AFS_2G:
            self.ares = 2.0/32768.0
        elif afs == AFS_4G:
            self.ares = 4.0/32768.0
        elif afs == AFS_8G:
            self.ares = 8.0/32768.0
        else: # afs == AFS_16G:
            self.ares = 16.0/32768.0

        if mfs == AK8963_BIT_14:
            self.mres = 4912.0/8190.0
        else: #  mfs == AK8963_BIT_16:
            self.mres = 4912.0/32760.0

        ## Configure MPU9250
        # sleep off
        self.bus.write_byte_data(self.address, PWR_MGMT_1, 0x00)
        time.sleep(0.1)
        # auto select clock source
        self.bus.write_byte_data(self.address, PWR_MGMT_1, 0x01)
        time.sleep(0.1)

        ## configure accelerometer
        # accel full scale select
        self.bus.write_byte_data(self.address, ACCEL_CONFIG, afs << 3)
        # gyro full scale select
        self.bus.write_byte_data(self.address, GYRO_CONFIG, gfs << 3)
        # A_DLPFCFG internal low pass filter for accelerometer to 10.2 Hz
        self.bus.write_byte_data(self.address, ACCEL_CONFIG_2, 0x05)
        # DLPF_CFG internal low pass filter for accelerometer to 10 Hz
        self.bus.write_byte_data(self.address, CONFIG, 0x05)
        """
        # sample rate divider
        self.bus.write_byte_data(self.address, SMPLRT_DIV, 0x04)
        """
        # magnetometer allow change to bypass multiplexer
        self.bus.write_byte_data(self.address, USER_CTRL, 0x00)
        time.sleep(0.01)

        # BYPASS_EN turn on bypass multiplexer
        self.bus.write_byte_data(self.address, INT_PIN_CFG, 0x02)
        time.sleep(0.1)

        # set read FuseROM mode
        self.bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x1F)
        time.sleep(0.1)

        # read coef data
        data = self.bus.read_i2c_block_data(AK8963_SLAVE_ADDRESS, AK8963_ASAX, 3)

        self.magXcoef = (data[0] - 128) / 256.0 + 1.0
        self.magYcoef = (data[1] - 128) / 256.0 + 1.0
        self.magZcoef = (data[2] - 128) / 256.0 + 1.0

        # set power down mode
        self.bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x00)
        time.sleep(0.1)

        # set scale&continous mode
        self.bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, (mfs<<4|mode))
        time.sleep(0.1)

    def read_accel_raw(self):
        """ Read accelerometer

        Returns:
            x, y, x (float float float) : g
        """
        data = self.bus.read_i2c_block_data(self.address, ACCEL_OUT, 6)
        x = self.conv_data(data[1], data[0])
        y = self.conv_data(data[3], data[2])
        z = self.conv_data(data[5], data[4])

        x = round(x*self.ares, 3)
        y = round(y*self.ares, 3)
        z = round(z*self.ares, 3)

        return x, y, z

    def read_gyro_raw(self):
        """ Read gyroscope

        Returns:
            x, y, z : (float float float) : rad/sec
        """
        data = self.bus.read_i2c_block_data(self.address, GYRO_OUT, 6)

        x = self.conv_data(data[1], data[0])
        y = self.conv_data(data[3], data[2])
        z = self.conv_data(data[5], data[4])

        x = round(x*self.gres, 3)
        y = round(y*self.gres, 3)
        z = round(z*self.gres, 3)

        return x, y, z

    def read_magnet_raw(self):
        """ Read magnetometer

        Returns:
            x, y, z (float float float) : in uT

        """
        x=0
        y=0
        z=0

        # wait until data ready and no overflow
        while self.bus.read_byte_data(AK8963_SLAVE_ADDRESS, AK8963_ST1) == 0x00:
            time.sleep(0.100)


        # read raw data (little endian)
        data = self.bus.read_i2c_block_data(AK8963_SLAVE_ADDRESS, AK8963_MAGNET_OUT, 7)

        # check overflow
        if (data[6] & 0x08)!=0x08:
            x = self.conv_data(data[0], data[1])
            y = self.conv_data(data[2], data[3])
            z = self.conv_data(data[4], data[5])

            x = round(x * self.mres * self.magXcoef, 3)
            y = round(y * self.mres * self.magYcoef, 3)
            z = round(z * self.mres * self.magZcoef, 3)

        return -y, -x, z

    def conv_data(self, data1, data2):
        """ Convert raw binary data to float

        Args:
            data1 (bits): LSB
            data2 (bits): MSB

        Returns:
            int16bit: MSB+LSB
        """
        value = data1 | (data2 << 8)
        if(value & (1 << 16 - 1)):
            value -= (1<<16)
        return value


    def read_magnet(self):
        """ Get a sample from magntometer with correction if calibrated.

        Returns:
            s (list) : The sample in uT, [x,y,z] (corrected if performed calibration).
        """
        x,y,z = self.read_magnet_raw()

        self.x_hist.insert(0, x)
        self.y_hist.insert(0, y)
        self.z_hist.insert(0, z)
        if len(self.x_hist) > 2500:
            self.x_hist.pop()
            self.y_hist.pop()
            self.z_hist.pop()
        self.max_x = max(self.x_hist)
        self.max_y = max(self.y_hist)
        self.max_z = max(self.z_hist)
        self.min_x = min(self.x_hist)
        self.min_y = min(self.y_hist)
        self.min_z = min(self.z_hist)

        x -= (self.max_x+self.min_x)/2
        y -= (self.max_y+self.min_y)/2
        z -= (self.max_z+self.min_z)/2

        if len(self.x_hist) > 1:
            x = float((x - self.min_x) / (self.max_x - self.min_x) * 2 - 1)
            y = float((y - self.min_y) / (self.max_y - self.min_y) * 2 - 1)
            z = float((z - self.min_z) / (self.max_z - self.min_z) * 2 - 1)


        return [x, y, z]


    def get_heading(self):
        """ Get magnetic heading

        Returns:
            heading (str) : Heading (N, NE, E, SE, S, SW, W, NW)
        """
        mag = self.read_magnet()
        x,y,z = self.read_accel_raw()
        acc = [x,y,z]

        #Normalize accelerometer raw values.
        accYnorm = acc[1]/math.sqrt(acc[1] * acc[1] + acc[2] * acc[2] + acc[0] * acc[0])
        accZnorm = acc[2]/math.sqrt(acc[1] * acc[1] + acc[2] * acc[2] + acc[0] * acc[0])

        #Calculate pitch and roll
        pitch = math.asin(accYnorm)
        roll = -math.asin(accZnorm/math.cos(pitch))

        #Calculate the new tilt compensated values
        magYcomp = mag[1]*math.cos(pitch)+mag[0]*math.sin(pitch)
        magZcomp = mag[1]*math.sin(roll)*math.sin(pitch)+mag[2]*math.cos(roll)+mag[0]*math.sin(roll)*math.cos(pitch)

        #Calculate heading
        heading = 180*math.atan2(magZcomp,magYcomp)/math.pi

        #Convert heading to 0 - 360
        if heading < 0:
            heading += 360;



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

m = MPU9250()

while True:
    print(m.get_heading())
