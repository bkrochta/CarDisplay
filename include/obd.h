#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <string.h>
#include <stdio.h>

#define ELM_ADDRESS "00:1D:A5:00:48:7A"

struct ObdData {
    int speed;
    double avg_speed;
    double dst;
} ;

int init_obd();
int get_speed(int *speed);
void get_average_speed(double *avg_speed, int *curr_speed);
void get_distance_traveled(double *dst, double *avg_speed);
int read_obd(char *response, size_t len);
int send_command(char *command, size_t command_len, char *response, size_t response_len);
int attempt_reconnect();