import smbus
import time
import numpy as np
import sys
from scipy import linalg
import pickle


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
AK8963_ST1        = 0x02
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
        self.configMPU9250(GFS_250, AFS_2G, AK8963_BIT_16, AK8963_MODE_C8HZ)

        # initialize values
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

    def configMPU9250(self, gfs, afs, mfs, mode):
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

    def readAccel(self):
        """ Read accelerometer

        Returns:
            x, y, x (float float float) : g
        """
        data = self.bus.read_i2c_block_data(self.address, ACCEL_OUT, 6)
        x = self.dataConv(data[1], data[0])
        y = self.dataConv(data[3], data[2])
        z = self.dataConv(data[5], data[4])

        x = round(x*self.ares, 3)
        y = round(y*self.ares, 3)
        z = round(z*self.ares, 3)

        return x, y, z

    def readGyro(self):
        """ Read gyroscope

        Returns:
            x, y, z : (float float float) : rad/sec
        """
        data = self.bus.read_i2c_block_data(self.address, GYRO_OUT, 6)

        x = self.dataConv(data[1], data[0])
        y = self.dataConv(data[3], data[2])
        z = self.dataConv(data[5], data[4])

        x = round(x*self.gres, 3)
        y = round(y*self.gres, 3)
        z = round(z*self.gres, 3)

        return x, y, z

    def readMagnet(self):
        """ Read magnetometer

        Returns:
            x, y, z (dictionary) : in uT

        """
        x=0
        y=0
        z=0

        # check data ready
        drdy = self.bus.read_byte_data(AK8963_SLAVE_ADDRESS, AK8963_ST1)
        if drdy & 0x01 :
            data = self.bus.read_i2c_block_data(AK8963_SLAVE_ADDRESS, AK8963_MAGNET_OUT, 7)

            # check overflow
            if (data[6] & 0x08)!=0x08:
                x = self.dataConv(data[0], data[1])
                y = self.dataConv(data[2], data[3])
                z = self.dataConv(data[4], data[5])

                x = round(x * self.mres * self.magXcoef, 3)
                y = round(y * self.mres * self.magYcoef, 3)
                z = round(z * self.mres * self.magZcoef, 3)

        return x, y, z

    def dataConv(self, data1, data2):
        """ Convert data to float

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

    def read(self):
        """ Get a sample.

        Returns:
            s (list) : The sample in uT, [x,y,z] (corrected if performed calibration).
        """
        x,y,z = self.readMagnet()
        s = np.array([x,y,z]).reshape(3, 1)
        s = np.dot(self.A_1, s - self.b)
        return [s[0,0], s[1,0], s[2,0]]

    def calibrate(self):
        """ Performs calibration. """

        print('Collecting samples (Ctrl-C to stop and perform calibration)')

        try:
            s = []
            n = 0
            while True:
                s.append(self.read())
                n += 1
                sys.stdout.write('\rTotal: %d' % n)
                sys.stdout.flush()
                time.sleep(.25)
        except KeyboardInterrupt:
            pass

        # ellipsoid fit
        s = np.array(s).T
        M, n, d = self.__ellipsoid_fit(s)

        # calibration parameters
        # note: some implementations of sqrtm return complex type, taking real
        M_1 = linalg.inv(M)
        self.b = -np.dot(M_1, n)
        self.A_1 = np.real(self.F / np.sqrt(np.dot(n.T, np.dot(M_1, n)) - d) * linalg.sqrtm(M))
        np.save('b', self.b)
        np.save('a', self.A_1)


    def __ellipsoid_fit(self, s):
        """ Estimate ellipsoid parameters from a set of points.

        Args:
            s : array_like
              The samples (M,N) where M=3 (x,y,z) and N=number of samples.

        Returns:
            M, n, d (array_like, array_like, float) : The ellipsoid parameters M, n, d.

        """

        # D (samples)
        print(s)
        D = np.array([s[0]**2., s[1]**2., s[2]**2.,
                      2.*s[1]*s[2], 2.*s[0]*s[2], 2.*s[0]*s[1],
                      2.*s[0], 2.*s[1], 2.*s[2], np.ones_like(s[0])])

        # S, S_11, S_12, S_21, S_22 (eq. 11)

        S = np.dot(D, D.T)
        S_11 = S[:6,:6]
        S_12 = S[:6,6:]
        S_21 = S[6:,:6]
        S_22 = S[6:,6:]

        # C (Eq. 8, k=4)
        C = np.array([[-1,  1,  1,  0,  0,  0],
                      [ 1, -1,  1,  0,  0,  0],
                      [ 1,  1, -1,  0,  0,  0],
                      [ 0,  0,  0, -4,  0,  0],
                      [ 0,  0,  0,  0, -4,  0],
                      [ 0,  0,  0,  0,  0, -4]])

        # v_1 (eq. 15, solution)
        E = np.dot(linalg.inv(C),
                   S_11 - np.dot(S_12, np.dot(linalg.inv(S_22), S_21)))

        E_w, E_v = np.linalg.eig(E)

        v_1 = E_v[:, np.argmax(E_w)]
        if v_1[0] < 0: v_1 = -v_1

        # v_2 (eq. 13, solution)
        v_2 = np.dot(np.dot(-np.linalg.inv(S_22), S_21), v_1)

        # quadric-form parameters
        M = np.array([[v_1[0], v_1[3], v_1[4]],
                      [v_1[3], v_1[1], v_1[5]],
                      [v_1[4], v_1[5], v_1[2]]])
        n = np.array([[v_2[0]],
                      [v_2[1]],
                      [v_2[2]]])
        d = v_2[3]

        return M, n, d

    def get_heading(self, heading):
        """ Get magnetic heading

        Args:
            heading (float) : Magentic direction (-180, 180) in degrees

        Returns:
            heading (str) : Heading (N, NE, E, SE, S, SW, W, NW)
        """
        if(heading <= -157.5):
            return "S"
        elif(heading < -112.5):
            return "SE"
        elif(heading <= -67.5):
            return "E"
        elif(heading < -22.5):
            return "NE"
        elif(heading <= 22.5):
            return "N"
        elif(heading < 67.5):
            return "NW"
        elif(heading <= 112.5):
            return "W"
        elif(heading < 157.5):
            return "SW"
        else:
            return "S"
