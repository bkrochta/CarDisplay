#include "obd.h"

int serial;
int connected = 0;

int init_obd(){
    char command[37], resp[256];
    struct termios tty;

    strncpy(command, "sudo rfcomm bind 0 ", 20);
    strncat(command, ELM_ADDRESS, 18);
    system(command);

    if ((serial = open("/dev/rfcomm0", O_RDWR | O_NOCTTY | O_SYNC)) < 0) {
        fprintf(stderr, "OBDII: Error opening serial device\n");
        return 1;
    }
    connected = 1;

    memset(&tty, 0, sizeof(tty));
    if(tcgetattr(serial, &tty) != 0){
        fprintf(stderr, "OBDII: Error from tcgetattr\n");
        return 2;
    }
    tty.c_cflag &= ~PARENB;
    tty.c_cflag &= ~CSTOPB;
    tty.c_cflag |= CS8;
    cfsetispeed(&tty, B38400);
    cfsetospeed(&tty, B38400);
    if(tcsetattr(serial, TCSANOW, &tty) != 0){
        fprintf(stderr, "OBDII: Error from tcsetaddr\n");
        return 3;
    }
    // initialize
    // reset
    if(send_command("ATZ\r", 4, resp, 256)){
        return 4;
    }
    printf("OBDII: ATZ response: %s\n", resp);

    // echo off
    if(send_command("ATE0\r", 5, resp, 256)){
        return 6;
    }
    printf("OBDII: ATE0 response: %s\n", resp);

    // headers off
    if(send_command("ATH0\r", 5, resp, 256)){
        return 8;
    }
    printf("OBDII: ATH0 response: %s\n", resp);

    // linefeeds off
    if(send_command("ATL0\r", 5, resp, 256)){
        return 10;
    }
    printf("OBDII: ATL0 response: %s\n", resp);

    return 0;
}

/*
** Command should already be appended with \r before calling
*/
int send_command(char *command, size_t command_len, char *response, size_t response_len){
    if(write(serial, command, command_len) != command_len){
        fprintf(stderr, "OBDII: Error writing command <%s>\n", command);
        return -1;
    }
    if (read_obd(response, response_len)){
        fprintf(stderr, "OBDII: Failed to read response from command <%s>\n", command);
        return -1;
    }
    return 0;
}

int read_obd(char *response, size_t len){
    char rec;
    int i = 0, ret;

    memset(response, 0, len);
    while(i < len){                                             // Dont overflow response
        ret = read(serial, &rec, 1);                            // read one byte
        if(ret != 1) return -1;                                 // Failed to read
        if(rec == '\r') continue;                               // skip \r from sending command
        if(rec == '>') break;                                   // End of response
        if(response[0] != 0 || rec != '>') response[i++] = rec; // Add char to reponse
    }
    return 0;
}

int get_speed(int *speed){
    char buff[32];
    int speed_kmh;

    if (send_command("010D\r", 5, buff, 32)){
        fprintf(stderr, "OBDII: Error getting speed.\n");
        return -1;
    }

    sscanf(buff, "41 0D %x", &speed_kmh);
    *speed = roundf(speed_kmh * 0.621371);

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

// int main(){
//     char command[100], buff[100];
//     int size, speed;
//     init_obd();
//     memset(command, 0, 100);
//     while(1){
//         scanf(" %s", command);
//         size = strlen(command);
//         if (strcmp(command, "speed")==0){
//             get_speed(&speed);
//             printf("Speed: %d\n", speed);
//         } else{
//             command[size] = '\r';
//             send_command(command, size+1, buff, 100);
//             printf("Response: <%s>\n", buff);
//         }
//         memset(command,0,100);
//         memset(buff,0,100);
//     }
    
//     return 0;
// }