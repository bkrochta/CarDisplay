#include "obd.h"

int serial;

int init_obd(){
    char command[37], resp[256];
    struct termios tty;

    strncpy(command, "sudo rfcomm bind 0 ", 20);
    strncat(command, ELM_ADDRESS, 18);
    system(command);
    sleep(1);

    if ((serial = open("dev/rfcomm0", O_RDWR)) < 0) {
        printf("error opening serial device\n");
        return 1;
    }

    memset(&tty, 0, sizeof(tty));
    if(tcgetattr(serial, &tty) != 0){
        printf("Error from tcgetattr\n");
        return 2;
    }
    tty.c_cflag &= ~PARENB;
    tty.c_cflag &= ~CSTOPB;
    tty.c_cflag |= CS8;
    cfsetispeed(&tty, B38400);
    cfsetospeed(&tty, B38400);
    if(tcsetattr(serial, TCSANOW, &tty) != 0){
        printf("Error from tcsetaddr\n");
        return 3;
    }
    // initialize
    if(write(serial, "ATZ\r", 4) != 4){
        printf("error writing ATZ\n");
        return 4;
    }
    sleep(1);
    if(read_obd(resp)){
        printf("Error reading obd\n");
        return 5;
    }
    printf("ATZ response: %s", resp);

    // echo off
    if(write(serial, "ATE0\r", 5) != 5){
        printf("error writing ATE0\n");
        return 6;
    }
    sleep(.1);
    if(read_obd(resp)){
        printf("Error reading obd\n");
        return 7;
    }
    printf("ATE0 response: %s", resp);
    // headers on
    if(write(serial, "ATH1\r", 5) != 5){
        printf("error writing ATH1\n");
        return 8;
    }
    sleep(.1);
    if(read_obd(resp)){
        printf("Error reading obd\n");
        return 9;
    }
    printf("ATH1 response: %s", resp);
    // linefeeds off
    if(write(serial, "ATL0\r", 5) != 5){
        printf("error writing ATL0\n");
        return 10;
    }
    sleep(.1);
    if(read_obd(resp)){
        printf("Error reading obd\n");
        return 11;
    }
    printf("ATL0 response: %s", resp);
    // read volt
    if(write(serial, "AT RV\r", 6) != 6){
        printf("error writing AT RV\n");
        return 12;
    }
    sleep(.1);
    if(read_obd(resp)){
        printf("Error reading obd\n");
        return 13;
    }
    printf("AT RV response: %s", resp);

    return 0;
}

int get_speed(int *speed){
    char buff[32];
    unsigned int temp;
    // read volt
    if(write(serial, "010D\r", 5) != 5){
        printf("error writing speed\n");
        return 14;
    }

    if(read_obd(buff)){
        printf("Error reading speed\n");
        return 15;
    }
    printf("Speed response: %s", buff);
    sscanf(buff, "48 6B 10 41 0D %x", &temp);

    *speed = roundf(temp * 0.621371);

    return 0;
}

void get_average_speed(int *avg_speed, int *curr_speed){
    static int count = 0;

    *avg_speed = ((avg_speed[0] * count) + curr_speed[0]) / (count + 1);
    count++;
}

void get_distance_traveled(int *dst, int *avg_speed){
    struct timespec time;
    clock_gettime(CLOCK_MONOTONIC,&time);
    static long start_time = 0;

    if (start_time == 0){
        start_time = time.tv_sec;
    }
    *dst = avg_speed[0] * roundf((time.tv_sec - start_time) / 3600.0f);
}

int read_obd(char *result){
    char rec;
    int i, ret, len;

    len = strlen(result);
    memset(result, 0, len);
    while(i < len){
        ret = read(serial, &rec, 1);
        if(ret != 1) return 1;
        if(rec == '\r') continue;
        if(rec == '>') break;
        if(result[0] != 0 || rec != '>') result[i++] = rec;
    }
    return 0;
}