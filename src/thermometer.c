#include "thermometer.h"

char filename[45] = {0};

void init_therm(){
    system("modprobe w1-gpio");
    system("modprobe w1-therm");
    
    strncpy(filename, "/sys/bus/w1/devices/", 21);
    strncat(filename, OUT_THERM_ADDR, 16);
    strncat(filename, "/w1_slave", 10);
}

/* Get temperature in F.
** Returns 0 on success
 */ 
int get_temp(int* temp){
    int fd;
    double temp_c;
    char buff[75], temp_raw[6];

    memset(buff, 0, 75);
    if((fd = open(filename, O_RDONLY)) < 0) {
        fprintf(stderr, "Thermometer: Failed to open therm file.\n");
        return 1;
    }

    if((read(fd, buff, 74)) != 74){
        fprintf(stderr, "Thermometer: Failed to read device file.\n");
        close(fd);
        return 2;
    }
    close(fd);

    memcpy(temp_raw, buff+69, 6);

    temp_c = atof(temp_raw) / 1000.0;
    *temp = (int) (temp_c * 9.0 / 5.0 + 32.0);

    return 0;
}