#include "mpu9250.h"

float mag_bias[] = {0,0,0};
float mag_scale[] = {0,0,0};
float accel_bias[] = {0,0,0};
float gyro_bias[] = {0,0,0};
float gres, ares, mres, magXcoef, magYcoef, magZcoef;
int bus;

void init_mpu(){
    int cal_data;
    char buff[66];
    if ((bus = open("/dev/i2c-1", O_RDWR)) < 0){
        printf("Failed to open i2c bus\n");
        exit(1);
    }

    config_mpu(GFS_250, AFS_2G, AK8963_BIT_16, AK8963_MODE_C100HZ);

    
    if ((cal_data = open("/home/pi/CarDisplay/calibration_data", O_RDONLY)) < 0){
        printf("Failed to open calibration data file\n");
        exit(3);
    }
    read(cal_data, buff, 65);
    sscanf(buff,"%f,%f,%f,%f,%f,%f", &mag_scale[0], &mag_scale[1], &mag_scale[2], &mag_bias[0], &mag_bias[1], &mag_bias[2]);
    
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
    // printf("reset\n");
    // data[0] = 0x80;
    // if(i2c_write(SLAVE_ADDRESS , PWR_MGMT_1, data, 1)) printf("failed\n");
    // sleep(0.1);
    printf("sleep off\n");
    data[0] = 0x00;
    if(i2c_write(SLAVE_ADDRESS , PWR_MGMT_1, data, 1)) printf("failed\n");
    sleep(0.1);
    ret = i2c_read(SLAVE_ADDRESS , WHO_AM_I, data, 1);
    printf("%d, %x\n",ret, data[0]);
    
    printf("auto select clock source\n");
    data[0] = 0x01;
    if(i2c_write(SLAVE_ADDRESS , PWR_MGMT_1, data, 1)) printf("failed\n");
    printf("turn on accel and gyro\n");
    data[0] = 0x00;
    if(i2c_write(SLAVE_ADDRESS , PWR_MGMT_2, data, 1)) printf("failed\n");
    sleep(0.1);

    printf("configure accelerometer\n");
    printf("accel full scale select\n");
    data[0] = afs << 3;
    if(i2c_write(SLAVE_ADDRESS , ACCEL_CONFIG, data, 1)) printf("failed\n");
    printf("gyro full scale select\n");
    data[0] = gfs << 3;
    if(i2c_write(SLAVE_ADDRESS , GYRO_CONFIG, data, 1)) printf("failed\n");
    printf("A_DLPFCFG internal low pass filter for accelerometer to 10.2 Hz\n");
    data[0] = 0x05;
    if(i2c_write(SLAVE_ADDRESS , ACCEL_CONFIG_2, data, 1)) printf("failed\n");
    printf("DLPF_CFG internal low pass filter for gyroscope to 10 Hz\n");
    data[0] = 0x05;
    if(i2c_write(SLAVE_ADDRESS , CONFIG, data, 1)) printf("failed\n");

    printf("sample rate divider\n");
    //if(i2c_write(SLAVE_ADDRESS , SMPLRT_DIV, 0x04, 1)) printf("failed\n");

    printf("magnetometer allow change to bypass multiplexer\n");
    data[0] = 0x00;
    if(i2c_write(SLAVE_ADDRESS , USER_CTRL, data, 1)) printf("failed\n");
    sleep(0.01);

    printf("BYPASS_EN turn on bypass multiplexer\n");
    data[0] = 0x02;
    if(i2c_write(SLAVE_ADDRESS , INT_PIN_CFG, data, 1)) printf("failed\n");
    sleep(0.1);

    printf("set power down mode\n");
    data[0] = 0x00;
    if(i2c_write(AK8963_SLAVE_ADDRESS , AK8963_CNTL1, data, 1)) printf("failed\n");
    sleep(0.1);

    printf("set read FuseROM mode\n");
    data[0] = 0x1F;
    if(i2c_write(AK8963_SLAVE_ADDRESS , AK8963_CNTL1, data, 1)) printf("failed\n");
    sleep(0.1);

    printf("read coef data\n");
    ret = i2c_read(AK8963_SLAVE_ADDRESS , AK8963_ASAX, data, 3);
    printf("%d\n", ret);

    magXcoef = (data[0] - 128) / 256.0 + 1.0;
    magYcoef = (data[1] - 128) / 256.0 + 1.0;
    magZcoef = (data[2] - 128) / 256.0 + 1.0;

    printf("set power down mode\n");
    data[0] = 0x00;
    if(i2c_write(AK8963_SLAVE_ADDRESS , AK8963_CNTL1, data, 1)) printf("failed\n");
    sleep(0.1);

    printf("set scale&continous mode\n");
    data[0] = (mfs<<4|mode);
    if(i2c_write(AK8963_SLAVE_ADDRESS , AK8963_CNTL1, data, 1)) printf("failed\n");

    sleep(0.1);
}

int read_accel_raw(__s16 *accel_raw){
    __u8 data[6];

    if (i2c_read(SLAVE_ADDRESS , ACCEL_OUT, data, 6)){
        printf("failed\n");
        return 1;
    }

    accel_raw[0] = conv_data(data[1], data[0]);
    accel_raw[1] = conv_data(data[3], data[2]);
    accel_raw[2] = conv_data(data[5], data[4]);

    return 0;
}

int read_gyro_raw(__s16 *gyro_raw){
    __u8 data[6];

    if ((i2c_read(SLAVE_ADDRESS , GYRO_OUT, data, 6)) < 0){
        printf("failed\n");
        return 1;
    }

    gyro_raw[0] = conv_data(data[1], data[0]);
    gyro_raw[1] = conv_data(data[3], data[2]);
    gyro_raw[2] = conv_data(data[5], data[4]);

    return 0;
}
int read_mag_raw(__s16 *mag_raw){
    __u8 data[7];

    do {
        if(i2c_read(AK8963_SLAVE_ADDRESS , AK8963_ST1, data, 1)) printf("failed\n");
    } while (data[0] == 0x00);

    printf("read raw data (little endian)\n");
    if ((i2c_read(AK8963_SLAVE_ADDRESS , AK8963_MAGNET_OUT, data, 7)) < 0){
        printf("failed\n");
        return 1;
    }

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
        printf("failed\n");
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
        printf("failed\n");
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

    if (read_mag_raw(mag_raw)){
        printf("failed\n");
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

void get_heading(char *direction){
    float mag[3];
    double heading;

    if(read_mag(mag)) {
        strcpy(direction, "NA");
    } else{
        heading = atan2(mag[0], -mag[1]);
        if (heading < 0)
            heading += 360;

        if(heading <= 22.5)
            strcpy(direction, "N");
        else if(heading < 67.5)
            strcpy(direction, "NE");
        else if(heading <= 112.5)
            strcpy(direction, "E");
        else if(heading < 157.5)
            strcpy(direction, "SE");
        else if(heading <= 202.5)
            strcpy(direction, "S");
        else if(heading < 247.5)
            strcpy(direction, "SW");
        else if(heading <= 292.5)
            strcpy(direction, "W");
        else if(heading < 337.5)
            strcpy(direction, "NW");
        else
            strcpy(direction, "N");
    }
}

__s16 conv_data(__u8 data1, __u8 data2) {
    __s16 value;

    value = data1 | (data2 << 8);
    if (value & ((1 << 16) - 1)){
        value -= (1 << 16);
    }

    return value;
}

int i2c_read(__u8 slave_addr, __u8 reg_addr, __u8 *data, __u8 length) {
    int count, ret, tries;

    if (i2c_write(slave_addr, reg_addr, NULL, 0)) {
        return 10;
    }

    count = 0;
    tries = 0;

    while ((count < length) && tries < 5) {
        if ((ret = read(bus, data + count, length - count)) < 0){
            printf("Failed to read I2C\n");
            return 8;
        }
        count += ret;

        if (count == length) break;

        sleep(.01);
        tries++;
    }
    if (count < length){
        printf("failed to read I2C\n");
        return 9;
    }

    return 0;
}

int i2c_write(__u8 slave_addr, __u8 reg_addr, __u8 *data, __u8 length){
    __u8 *buff;

    if (ioctl(bus, I2C_SLAVE, slave_addr) < 0) {
        printf("Failed to open slave address\n");
        return 10;
    }
    if (length == 0){
        if ((write(bus, &reg_addr, 1)) != 1){
            printf("Failed to write register\n");
            return 11;
        }
    } else{
        buff = (__u8 *) calloc(1, length + 1);
        buff[0] = reg_addr;
        memcpy(buff + 1, data, length);

        if ((write(bus, buff, length + 1)) != length + 1){
            printf("Failed to write to register\n");
            free(buff);
            return 12;
        }
        free(buff);
    }

    return 0;
}