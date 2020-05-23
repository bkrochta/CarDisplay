#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>

#define OUT_THERM_ADDR "28-0315977942f6"

void init();
int get_temp();