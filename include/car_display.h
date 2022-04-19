#include "mpu9250.h"
#include "obd.h"
#include "thermometer.h"
#include <gtk/gtk.h>
#include <pthread.h>
#include <stdlib.h>

#define LAYOUT_FILE "layout.glade"

struct update_data{
    GtkWidget *direction, *time, *temp, *speed, *a_speed, *dst;
} ;

void *thermometer_thread(void *args);
void *obd_thread(void *args);
void *compass_thread(void *args);
int update(gpointer data);