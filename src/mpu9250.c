#include "mpu9250.h"

float mag_bias[] = {0,0,0};
float mag_scale[] = {0,0,0};
float accel_bias[] = {0,0,0};
float gyro_bias[] = {0,0,0};
float gres, ares, mres, magXcoef, magYcoef, magZcoef;
int bus;

void init_mpu(int calibrate){
    int cal_data;
    char buff[66];
    if ((bus = open("/dev/i2c-1", O_RDWR)) < 0){
        printf("Failed to open i2c bus\n");
        exit(1);
    }
    if (ioctl(bus, I2C_SLAVE, SLAVE_ADDRESS) < 0) {
        printf("Failed to open mpu9250\n");
        exit(2);
    }
    config_mpu(GFS_250, AFS_2G, AK8963_BIT_16, AK8963_MODE_C100HZ);

    if(calibrate){
        calibrate_mag();
    } else{
        if ((cal_data = open("/home/pi/CarDisplay/calibration_data", O_RDONLY)) < 0){
            printf("Failed to open calibration data file\n");
            exit(3);
        }
        read(cal_data, buff, 65);
        sscanf(buff,"%f,%f,%f,%f,%f,%f", &mag_scale[0], &mag_scale[1], &mag_scale[2], &mag_bias[0], &mag_bias[1], &mag_bias[2]);
    }
}
void config_mpu(__u8 gfs, __u8 afs, __u8 mfs, __u8 mode){
    __u8 data[3];
    int ret;
    
    if (gfs == GFS_250)
        gres = 250.0/32768.0;
    else if (gfs == GFS_500)
        gres = 500.0/32768.0;
    else if (gfs == GFS_1000)
        gres = 1000.0/32768.0;
    else  // gfs == GFS_2000
        gres = 2000.0/32768.0;

    if (afs == AFS_2G)
        ares = 2.0/32768.0;
    else if (afs == AFS_4G)
        ares = 4.0/32768.0;
    else if (afs == AFS_8G)
        ares = 8.0/32768.0;
    else // afs == AFS_16G:
        ares = 16.0/32768.0;

    if (mfs == AK8963_BIT_14)
        mres = 4912.0/8190.0;
    else //  mfs == AK8963_BIT_16:
        mres = 4912.0/32760.0;

    printf("Configure MPU9250\n");
    printf("sleep off\n");
    i2c_smbus_write_byte_data(bus, PWR_MGMT_1, 0x00);
    sleep(0.1);
    printf("auto select clock source\n");
    i2c_smbus_write_byte_data(bus, PWR_MGMT_1, 0x01);
    sleep(0.1);

    printf("configure accelerometer\n");
    printf("accel full scale select\n");
    i2c_smbus_write_byte_data(bus, ACCEL_CONFIG, afs << 3);
    printf("gyro full scale select\n");
    i2c_smbus_write_byte_data(bus, GYRO_CONFIG, gfs << 3);
    printf("A_DLPFCFG internal low pass filter for accelerometer to 10.2 Hz\n");
    i2c_smbus_write_byte_data(bus, ACCEL_CONFIG_2, 0x05);
    printf("DLPF_CFG internal low pass filter for gyroscope to 10 Hz\n");
    i2c_smbus_write_byte_data(bus, CONFIG, 0x05);

    printf("sample rate divider\n");
    //i2c_smbus_write_byte_data(bus, SMPLRT_DIV, 0x04);

    printf("magnetometer allow change to bypass multiplexer\n");
    i2c_smbus_write_byte_data(bus, USER_CTRL, 0x00);
    sleep(0.01);

    printf("BYPASS_EN turn on bypass multiplexer\n");
    i2c_smbus_write_byte_data(bus, INT_PIN_CFG, 0x02);
    sleep(0.1);

    printf("set power down mode\n");
    i2c_smbus_write_byte_data(bus, AK8963_CNTL1, 0x00);
    sleep(0.1);

    printf("set read FuseROM mode\n");
    i2c_smbus_write_byte_data(bus, AK8963_CNTL1, 0x1F);
    sleep(0.1);

    printf("read coef data\n");
    ioctl(bus, I2C_SLAVE, AK8963_SLAVE_ADDRESS);
    ret = i2c_smbus_read_block_data(bus, AK8963_ASAX, &data);

    magXcoef = (data[0] - 128) / 256.0 + 1.0;
    magYcoef = (data[1] - 128) / 256.0 + 1.0;
    magZcoef = (data[2] - 128) / 256.0 + 1.0;

    printf("set power down mode\n");
    i2c_smbus_write_byte_data(bus, AK8963_CNTL1, 0x00);
    sleep(0.1);

    printf("set scale&continous mode\n");
    i2c_smbus_write_byte_data(bus, AK8963_CNTL1, (mfs<<4|mode));
    ioctl(bus, I2C_SLAVE, SLAVE_ADDRESS);

    sleep(0.1);
}

int read_accel_raw(__s16 *accel_raw){
    __u8 data[6];

    if ((i2c_smbus_read_block_data(bus, ACCEL_OUT, data)) < 0){
        return 1;
    }

    accel_raw[0] = conv_data(data[1], data[0]);
    accel_raw[1] = conv_data(data[3], data[2]);
    accel_raw[2] = conv_data(data[5], data[4]);

    return 0;
}

int read_gyro_raw(__s16 *gyro_raw){
    __u8 data[6];

    if ((i2c_smbus_read_block_data(bus, GYRO_OUT, data)) < 0){
        return 1;
    }

    gyro_raw[0] = conv_data(data[1], data[0]);
    gyro_raw[1] = conv_data(data[3], data[2]);
    gyro_raw[2] = conv_data(data[5], data[4]);

    return 0;
}
int read_mag_raw(__s16 *mag_raw){
    __u8 data[7];

    ioctl(bus, I2C_SLAVE, AK8963_SLAVE_ADDRESS);

    while ((i2c_smbus_read_byte_data(AK8963_SLAVE_ADDRESS, AK8963_ST1)) == 0x00){
        continue;
    }

    printf("read raw data (little endian)\n");
    if ((i2c_smbus_read_block_data(bus, AK8963_MAGNET_OUT, data)) < 0){
        ioctl(bus, I2C_SLAVE, SLAVE_ADDRESS);
        return 1;
    }
    ioctl(bus, I2C_SLAVE, SLAVE_ADDRESS);

    printf("check overflow\n");
    if ((data[6] & 0x08) != 0x08){
        mag_raw[0] = conv_data(data[0], data[1]);
        mag_raw[1] = conv_data(data[2], data[3]);
        mag_raw[2] = conv_data(data[4], data[5]);

        return 0;
    } else{ // overflow
        memset(mag_raw, 0x00, 6);

        return 0;
    }
}
int read_accel(float *accel){
    __s16 accel_raw[3];

    if (read_accel_raw(accel_raw)){
        return 1;
    }

    accel[0] = accel_raw[0] * ares;
    accel[1] = accel_raw[1] * ares;
    accel[2] = accel_raw[2] * ares;

    return 0;
}

int read_gyro(float *gyro){
    __s16 gyro_raw[3];

    if (read_gyro_raw(gyro_raw)){
        return 1;
    }

    gyro_raw[0] -= gyro_bias[0];
    gyro_raw[1] -= gyro_bias[1];
    gyro_raw[2] -= gyro_bias[2];

    gyro[0] = gyro_raw[0] * gres;
    gyro[1] = gyro_raw[1] * gres;
    gyro[2] = gyro_raw[2] * gres;

    return 0;
}

int read_mag(float *mag){
    __s16 mag_raw[3];
    float mag_temp[3];

    if (read_gyro_raw(mag_raw)){
        return 1;
    }

    mag_temp[0] = mag_raw[0] - mag_bias[0];
    mag_temp[1] = mag_raw[1] - mag_bias[1];
    mag_temp[2] = mag_raw[2] - mag_bias[2];

    mag_temp[0] *= mag_scale[0];
    mag_temp[1] *= mag_scale[1];
    mag_temp[2] *= mag_scale[2];

    mag[1] = mag_temp[0] * mres * magXcoef;
    mag[0] = mag_temp[1] * mres * magYcoef;
    mag[2] = 0 - (mag_temp[2] * mres * magZcoef);

    return 0;
}

void calibrate_accel_gyro(){

}

void calibrate_mag(){

}

void get_heading(char *direction);

__s16 conv_data(__u8 data1, __u8 data2) {
    __s16 value;

    value = data1 | (data2 << 8);
    if (value & ((1 << 16) - 1)){
        value -= (1 << 16);
    }

    return value;
}