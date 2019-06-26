import smbus
import time
import numpy as np
import math
import sys


### https:#www.invensense.com/wp-content/uploads/2015/02/RM-MPU-9250A-00-v1.6.pdf
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
        self.config(GFS_250, AFS_2G, AK8963_BIT_16, AK8963_MODE_C100HZ)

        # initialize values
        self.mag_bias = [0,0,0]
        self.mag_scale = [0,0,0]

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

        # sample rate divider
        self.bus.write_byte_data(self.address, SMPLRT_DIV, 0x04)

        # magnetometer allow change to bypass multiplexer
        self.bus.write_byte_data(self.address, USER_CTRL, 0x00)
        time.sleep(0.01)

        # BYPASS_EN turn on bypass multiplexer
        self.bus.write_byte_data(self.address, INT_PIN_CFG, 0x02)
        time.sleep(0.1)

        # set power down mode
        self.bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x00)
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

        x = round(x*self.gres, 3)#-3.262
        y = round(y*self.gres, 3)#+.03
        z = round(z*self.gres, 3)#+.604

        return x, y, z

    def read_magnet_raw(self):
        """ Read magnetometer
        Returns:
            x, y, z (float float float) : in uT
        """
        # wait until data ready and no overflow
        while self.bus.read_byte_data(AK8963_SLAVE_ADDRESS, AK8963_ST1) == 0x00:
            continue

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

            return y, x, -z
        else: # overflow
            return 0,0,0

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
        x -= self.mag_bias[0]
        y -= self.mag_bias[1]
        z -= self.mag_bias[2]

        x *= self.mag_scale[0]
        y *= self.mag_scale[1]
        z *= self.mag_scale[2]

        return [x, y, z]

    def calibrate(self):
        """ Calibrates magnetometer. Updates mag_bias and mag_scale.
        Returns:
            void
        """
        print('Collecting samples (Ctrl-C to stop and perform calibration)')
        try:
            s = []
            n = 0
            while True:
                s.append(self.read_magnet_raw())
                n += 1
                sys.stdout.write('\rTotal: %d' % n)
                sys.stdout.flush()
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass

        max_x = -32760
        max_y = -32760
        max_z = -32760
        min_x = 32760
        min_y = 32760
        min_z = 32760

        for trio in s:
            if trio[0] > max_x:
                max_x = trio[0]
            if trio[0] < min_x:
                min_x = trio[0]
            if trio[1] > max_y:
                max_y = trio[1]
            if trio[1] < min_y:
                min_y = trio[1]
            if trio[2] > max_z:
                max_z = trio[2]
            if trio[2] < min_z:
                min_z = trio[2]

        self.mag_bias[0]  = (max_x + min_x)/2;  # get average x mag bias in counts
        self.mag_bias[1]  = (max_y + min_y)/2;  # get average y mag bias in counts
        self.mag_bias[2]  = (max_z + min_z)/2;  # get average z mag bias in counts

        self.mag_scale[0]  = (max_x - min_x) / 2;
        # Get average y axis max chord length in counts
        self.mag_scale[1]  = (max_y - min_y) / 2;
        # Get average z axis max chord length in counts
        self.mag_scale[2]  = (max_z - min_z) / 2;

        avg_rad = self.mag_scale[0] + self.mag_scale[1] + self.mag_scale[2];
        avg_rad /= 3.0;

        self.mag_scale[0] = avg_rad / (float(self.mag_scale[0]));
        self.mag_scale[1] = avg_rad / (float(self.mag_scale[1]));
        self.mag_scale[2] = avg_rad / (float(self.mag_scale[2]));


    def get_heading(self):
        """ Get magnetic heading
        Returns:
            heading (str) : Heading (N, NE, E, SE, S, SW, W, NW)
        """
        mag = self.read_magnet()
        x,y,z = self.read_accel_raw()
        acc = [x,y,z]
        heading = math.atan2(mag[1],mag[2])*(180/math.pi)
        # if heading < 0:
        #     heading += 360
        #
        # print('not compensated %f ' % heading)
        #
        # #Normalize accelerometer raw values.
        # accYnorm = acc[1]/math.sqrt(acc[1] * acc[1] + acc[2] * acc[2] + acc[0] * acc[0])
        # accZnorm = acc[2]/math.sqrt(acc[1] * acc[1] + acc[2] * acc[2] + acc[0] * acc[0])
        #
        # #Calculate pitch and roll
        # pitch = math.asin(accYnorm)
        # roll = -math.asin(accZnorm/math.cos(pitch))
        #
        # #Calculate the new tilt compensated values
        # magYcomp = mag[1]*math.cos(pitch)+mag[0]*math.sin(pitch)
        # magZcomp = mag[1]*math.sin(roll)*math.sin(pitch)+mag[2]*math.cos(roll)+mag[0]*math.sin(roll)*math.cos(pitch)
        #
        # #Calculate heading
        # heading = 180*math.atan2(magZcomp,magYcomp)/math.pi

        #Convert heading to 0 - 360
        if heading < 0:
            heading += 360;
        #return heading

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


#===============================================================================
# Quaternion tests

#-------------------------------------------------------------------------------
# Definitions

sampleFreq = 9.6	# sample frequency in Hz
betaDef	= .1		# 2 * proportional gain

#-------------------------------------------------------------------------------
# Variable definitions

beta = betaDef								# 2 * proportional gain (Kp)
q0 = 1.0
q1 = 0.0
q2 = 0.0
q3 = 0.0	# quaternion of sensor frame relative to auxiliary frame


#-------------------------------------------------------------------------------
# AHRS algorithm update

def MadgwickAHRSupdate(gx, gy, gz, ax, ay, az, mx, my, mz):
    global q0, q1, q2, q3

	# Use IMU algorithm if magnetometer measurement invalid (avoids NaN in magnetometer normalisation)
    if (mx == 0.0) and (my == 0.0) and (mz == 0.0):
        MadgwickAHRSupdateIMU(gx, gy, gz, ax, ay, az)
        return


    # Rate of change of quaternion from gyroscope
    qDot1 = 0.5 * (-q1 * gx - q2 * gy - q3 * gz)
    qDot2 = 0.5 * (q0 * gx + q2 * gz - q3 * gy)
    qDot3 = 0.5 * (q0 * gy - q1 * gz + q3 * gx)
    qDot4 = 0.5 * (q0 * gz + q1 * gy - q2 * gx)

    # Compute feedback only if accelerometer measurement valid (avoids NaN in accelerometer normalisation)
    if not ((ax == 0.0) and (ay == 0.0) and (az == 0.0)):

        # Normalise accelerometer measurement
        recipNorm = invSqrt(ax * ax + ay * ay + az * az)
        ax *= recipNorm
        ay *= recipNorm
        az *= recipNorm

        # Normalise magnetometer measurement
        recipNorm = invSqrt(mx * mx + my * my + mz * mz)
        mx *= recipNorm
        my *= recipNorm
        mz *= recipNorm

		# Auxiliary variables to avoid repeated arithmetic
        _2q0mx = 2.0 * q0 * mx
        _2q0my = 2.0 * q0 * my
        _2q0mz = 2.0 * q0 * mz
        _2q1mx = 2.0 * q1 * mx
        _2q0 = 2.0 * q0
        _2q1 = 2.0 * q1
        _2q2 = 2.0 * q2
        _2q3 = 2.0 * q3
        _2q0q2 = 2.0 * q0 * q2
        _2q2q3 = 2.0 * q2 * q3
        q0q0 = q0 * q0
        q0q1 = q0 * q1
        q0q2 = q0 * q2
        q0q3 = q0 * q3
        q1q1 = q1 * q1
        q1q2 = q1 * q2
        q1q3 = q1 * q3
        q2q2 = q2 * q2
        q2q3 = q2 * q3
        q3q3 = q3 * q3

		# Reference direction of Earth's magnetic field
        hx = mx * q0q0 - _2q0my * q3 + _2q0mz * q2 + mx * q1q1 + _2q1 * my * q2 + _2q1 * mz * q3 - mx * q2q2 - mx * q3q3
        hy = _2q0mx * q3 + my * q0q0 - _2q0mz * q1 + _2q1mx * q2 - my * q1q1 + my * q2q2 + _2q2 * mz * q3 - my * q3q3
        _2bx = math.sqrt(hx * hx + hy * hy)
        _2bz = -_2q0mx * q2 + _2q0my * q1 + mz * q0q0 + _2q1mx * q3 - mz * q1q1 + _2q2 * my * q3 - mz * q2q2 + mz * q3q3
        _4bx = 2.0 * _2bx
        _4bz = 2.0 * _2bz

		# Gradient decent algorithm corrective step
        s0 = -_2q2 * (2.0 * q1q3 - _2q0q2 - ax) + _2q1 * (2.0 * q0q1 + _2q2q3 - ay) - _2bz * q2 * (_2bx * (0.5 - q2q2 - q3q3) + _2bz * (q1q3 - q0q2) - mx) + (-_2bx * q3 + _2bz * q1) * (_2bx * (q1q2 - q0q3) + _2bz * (q0q1 + q2q3) - my) + _2bx * q2 * (_2bx * (q0q2 + q1q3) + _2bz * (0.5 - q1q1 - q2q2) - mz)
        s1 = _2q3 * (2.0 * q1q3 - _2q0q2 - ax) + _2q0 * (2.0 * q0q1 + _2q2q3 - ay) - 4.0 * q1 * (1 - 2.0 * q1q1 - 2.0 * q2q2 - az) + _2bz * q3 * (_2bx * (0.5 - q2q2 - q3q3) + _2bz * (q1q3 - q0q2) - mx) + (_2bx * q2 + _2bz * q0) * (_2bx * (q1q2 - q0q3) + _2bz * (q0q1 + q2q3) - my) + (_2bx * q3 - _4bz * q1) * (_2bx * (q0q2 + q1q3) + _2bz * (0.5 - q1q1 - q2q2) - mz)
        s2 = -_2q0 * (2.0 * q1q3 - _2q0q2 - ax) + _2q3 * (2.0 * q0q1 + _2q2q3 - ay) - 4.0 * q2 * (1 - 2.0 * q1q1 - 2.0 * q2q2 - az) + (-_4bx * q2 - _2bz * q0) * (_2bx * (0.5 - q2q2 - q3q3) + _2bz * (q1q3 - q0q2) - mx) + (_2bx * q1 + _2bz * q3) * (_2bx * (q1q2 - q0q3) + _2bz * (q0q1 + q2q3) - my) + (_2bx * q0 - _4bz * q2) * (_2bx * (q0q2 + q1q3) + _2bz * (0.5 - q1q1 - q2q2) - mz)
        s3 = _2q1 * (2.0 * q1q3 - _2q0q2 - ax) + _2q2 * (2.0 * q0q1 + _2q2q3 - ay) + (-_4bx * q3 + _2bz * q1) * (_2bx * (0.5 - q2q2 - q3q3) + _2bz * (q1q3 - q0q2) - mx) + (-_2bx * q0 + _2bz * q2) * (_2bx * (q1q2 - q0q3) + _2bz * (q0q1 + q2q3) - my) + _2bx * q1 * (_2bx * (q0q2 + q1q3) + _2bz * (0.5 - q1q1 - q2q2) - mz)
        recipNorm = invSqrt(s0 * s0 + s1 * s1 + s2 * s2 + s3 * s3) # normalise step magnitude
        s0 *= recipNorm
        s1 *= recipNorm
        s2 *= recipNorm
        s3 *= recipNorm

		# Apply feedback step
        qDot1 -= beta * s0
        qDot2 -= beta * s1
        qDot3 -= beta * s2
        qDot4 -= beta * s3


	# Integrate rate of change of quaternion to yield quaternion
    q0 += qDot1 * (1.0 / sampleFreq)
    q1 += qDot2 * (1.0 / sampleFreq)
    q2 += qDot3 * (1.0 / sampleFreq)
    q3 += qDot4 * (1.0 / sampleFreq)

	# Normalise quaternion
    recipNorm = invSqrt(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3)
    q0 *= recipNorm
    q1 *= recipNorm
    q2 *= recipNorm
    q3 *= recipNorm


def invSqrt(number):
    threehalfs = 1.5
    x2 = number * 0.5
    y = np.float32(number)

    i = y.view(np.int32)
    i = np.int32(0x5f3759df) - np.int32(i >> 1)
    y = i.view(np.float32)

    y = y * (threehalfs - (x2 * y * y))
    return float(y)

def toEulerAngle(q0, q1, q2, q3):
	#roll (x-axis rotation)
    sinr_cosp = 2.0 * (q0 * q1 + q2 * q3)
    cosr_cosp = 1.0 - 2.0 * (q1 * q1 + q2 * q2)
    roll = math.atan2(sinr_cosp, cosr_cosp)

	# pitch (y-axis rotation)
    sinp = 2.0 * (q0 * q2 - q3 * q1)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp) # use 90 degrees if out of range
    else:
        pitch = math.asin(sinp)

	# yaw (z-axis rotation)
    siny_cosp = 2.0 * (q0 * q3 + q1 * q2)
    cosy_cosp = 1.0 - 2.0 * (q2 * q2 + q3 * q3)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return pitch, roll, yaw

#===============================================================================

m = MPU9250()
m.calibrate()
timestart = time.perf_counter()
count=0
xt,yt,zt=0,0,0

while True:
    # print(time.perf_counter()-timestart)
    # timestart = time.perf_counter()
    #print(m.read_accel_raw())
    # x,y,z=m.read_gyro_raw()
    # xt+=x
    # yt+=y
    # zt+=z
    # count+=1
    # print('x:',xt/count)
    # print('y:',yt/count)
    # print('z:',zt/count)

    #print(m.read_gyro_raw())
    #print(m.read_magnet())
    print(m.get_heading())
    #print()

    # ax,ay,az = m.read_accel_raw()
    # gx,gy,gz = m.read_gyro_raw()
    # mx,my,mz = m.read_magnet_raw()
    # MadgwickAHRSupdate(gx, gy, gz, ax, ay, az, mx, my, mz)
    # pitch, roll, yaw = toEulerAngle(q0, q1, q2, q3)
    # # print(q0)
    # # print(q1)
    # # print(q2)
    # # print(q3)
    # print(pitch)
    # print(roll)
    # print(yaw)
    # print()


    time.sleep(.01)
