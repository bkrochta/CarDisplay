#include "mpu9250.h"

double mag_bias[] = {0,0,0};
double mag_scale[] = {0,0,0};

void init(int calibrate){
    config(GFS_250, AFS_2G, AK8963_BIT_16, AK8963_MODE_C100HZ);

    if(calibrate){
        calibrate_mag();
    } else{
        
    }
}
void config(unsigned char gfs, unsigned char afs, unsigned char mfd, unsigned char mode);
void read_accel_raw(double *ax, double *ay, double *az);
void read_gyro_raw(double *gx, double *gy, double *gz);
void read_mag_raw(double *mx, double *my, double *mz);
void read_accel(double *ax, double *ay, double *az);
void read_gyro(double *gx, double *gy, double *gz);
void read_mag(double *mx, double *my, double *mz);
void calibrate_accel_gyro();
void calibrate_mag();
void get_heading(char *direction);
double conv_data(unsigned char data1, unsigned char data2);