#include "thermometer.h"

void init_therm(){
    system("modprobe w1-gpio");
    system("modprobe w1-therm");
}

int get_temp(){
    int fd,  temp_f;
    double temp_c;
    char buff[75], temp_raw[6], filename[45];

    strncpy(filename, "/sys/bus/w1/devices/", 20);
    strncat(filename, OUT_THERM_ADDR, 16);
    strncat(filename, "/w1_slave", 10);

    if((fd = open(filename, O_RDONLY)) < 0) {
        printf("Failed to open therm file\n");
        return -100;
    }

    if((read(fd, buff, 74)) != 74){
        printf("Failed to read device file\n");
        return -100;
    }
    temp_raw[0] = buff[69];
	temp_raw[1] = buff[70];
	temp_raw[2] = buff[71];
	temp_raw[3] = buff[72];
	temp_raw[4] = buff[73];
	temp_raw[5] = buff[74];

    temp_c = atof(temp_raw) / 1000.0;
    temp_f = (int) (temp_c * 9.0 / 5.0 + 32.0);

    return temp_f;
}