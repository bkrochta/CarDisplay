#include "mpu9250.h"
#include "obd.h"
#include "thermometer.h"
#include <gtk/gtk.h>
#include <pthread.h>
#include <stdlib.h>
#include <math.h>
#include <stdatomic.h>

#define LAYOUT_FILE "/home/pi/CarDisplay1/layout.glade"

struct GuiLabels {
    GtkWidget *direction, *time, *temp, *speed, *a_speed, *dst;
} ;

gboolean update_thermometer_gui(gpointer update_data);
void *thermometer_thread(void *args);
gboolean update_obd_gui(gpointer update_data);
void *obd_thread(void *args);
gboolean update_compass_gui(gpointer update_data);
void *compass_thread(void *args);
gboolean update_clock_gui(gpointer data);
static gboolean check_escape(GtkWidget *widget, GdkEventKey *event, gpointer data);