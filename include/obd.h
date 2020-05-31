#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <string.h>
#include <stdio.h>

#define ELM_ADDRESS "00:1D:A5:00:48:7A"

int init_obd();
int get_speed(int *speed);
void get_average_speed(int *avg_speed, int *curr_speed);
void get_distance_traveled(int *dst, int *avg_speed);
int read_obd(char *result);