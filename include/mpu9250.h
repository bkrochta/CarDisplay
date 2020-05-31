#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <linux/types.h>
#include <math.h>

// https:#www.invensense.com/wp-content/uploads/2015/02/RM-MPU-9250A-00-v1.6.pdf
// MPU9250 Default I2C slave address
#define SLAVE_ADDRESS 0x68
// AK8963 I2C slave address
#define AK8963_SLAVE_ADDRESS 0x0C
// Device id
#define DEVICE_ID 0x71

/* MPU-9250 Register Addresses */
#define XG_OFFSET_H 0x13  // User-defined trim values for gyroscope
#define XG_OFFSET_L 0x14
#define YG_OFFSET_H 0x15
#define YG_OFFSET_L 0x16
#define ZG_OFFSET_H 0x17
#define ZG_OFFSET_L 0x18
// sample rate driver
#define SMPLRT_DIV 0x19
#define CONFIG 0x1A
#define GYRO_CONFIG 0x1B
#define ACCEL_CONFIG 0x1C
#define ACCEL_CONFIG_2 0x1D
#define LP_ACCEL_ODR 0x1E
#define WOM_THR 0x1F

#define FIFO_EN 0x23
#define I2C_MST_CTRL 0x24
#define I2C_MST_STATUS 0x36
#define INT_PIN_CFG 0x37
#define INT_ENABLE 0x38
#define INT_STATUS 0x3A
#define ACCEL_OUT 0x3B
#define TEMP_OUT 0x41
#define GYRO_OUT 0x43
#define FIFO_COUNTH 0x72
#define FIFO_COUNTL 0x73
#define FIFO_R_W 0x74
#define XA_OFFSET_H 0x77
#define XA_OFFSET_L 0x78
#define YA_OFFSET_H 0x7A
#define YA_OFFSET_L 0x7B
#define ZA_OFFSET_H 0x7D
#define ZA_OFFSET_L 0x7E

#define I2C_MST_DELAY_CTRL 0x67
#define SIGNAL_PATH_RESET 0x68
#define MOT_DETECT_CTRL 0x69
#define USER_CTRL 0x6A
#define PWR_MGMT_1 0x6B
#define PWR_MGMT_2 0x6C
#define FIFO_R_W 0x74
#define WHO_AM_I 0x75

// Gyro Full Scale Select 250dps
#define GFS_250 0x00
// Gyro Full Scale Select 500dps
#define GFS_500 0x01
// Gyro Full Scale Select 1000dps
#define GFS_1000 0x02
// Gyro Full Scale Select 2000dps
#define GFS_2000 0x03
// Accel Full Scale Select 2G
#define AFS_2G 0x00
// Accel Full Scale Select 4G
#define AFS_4G 0x01
// Accel Full Scale Select 8G
#define AFS_8G 0x02
// Accel Full Scale Select 16G
#define AFS_16G 0x03

// AK8963 Register Addresses
#define AK8963_ST1 0x02 // data ready register
#define AK8963_MAGNET_OUT 0x03
#define AK8963_CNTL1 0x0A
#define AK8963_CNTL2 0x0B
#define AK8963_ASAX 0x10

// CNTL1 Mode select
// Power down mode
#define AK8963_MODE_DOWN 0x00
// One shot data output
#define AK8963_MODE_ONE 0x01

// Continous data output 8Hz
#define AK8963_MODE_C8HZ 0x02
// Continous data output 100Hz
#define AK8963_MODE_C100HZ 0x06

// Magneto Scale Select
// 14bit output
#define AK8963_BIT_14 0x00
// 16bit output
#define AK8963_BIT_16 0x01

void init_mpu();
void config_mpu(__u8 gfs, __u8 afs, __u8 mfs, __u8 mode);
int read_accel_raw(__s16 *accel_raw);
int read_gyro_raw(__s16 *gyro_raw);
int read_mag_raw(__s16 *mag_raw);
int read_accel(float *accel);
int read_gyro(float *gyro);
int read_mag(float *mag);
void get_heading(char *direction);
__s16 conv_data(__u8 data1, __u8 data2);
int i2c_read(__u8 slave_addr, __u8 reg_addr, __u8 *data, __u8 length);
int i2c_write(__u8 slave_addr, __u8 reg_addr, __u8 *data, __u8 length);
