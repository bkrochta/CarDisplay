#include "car_display.h"

pthread_mutex_t mutex_therm, mutex_obd, mutex_compass;
int run=1, temperature, current_speed;
double average_speed, distance_traveled;
char curr_direction[3];

int main(int argc, char **argv){
    GtkWidget *window, *direction, *time, *temp, *speed, *a_speed, *dst;
    pthread_t thread_therm, thread_obd, thread_compass;
    struct update_data data;
    GdkRGBA color = {0,0,0,1};
    GtkBuilder *builder;

    gtk_init(&argc, &argv);

    builder = gtk_builder_new();
    gtk_builder_add_from_file(builder, LAYOUT_FILE, NULL);

    window = GTK_WIDGET(gtk_builder_get_object (builder, "window"));

    direction = GTK_WIDGET(gtk_builder_get_object (builder, "dir_label"));
    time = GTK_WIDGET(gtk_builder_get_object (builder, "clock_label"));
    temp = GTK_WIDGET(gtk_builder_get_object (builder, "temp_label"));
    speed = GTK_WIDGET(gtk_builder_get_object (builder, "speed_label"));
    a_speed = GTK_WIDGET(gtk_builder_get_object (builder, "avg_speed_label"));
    dst = GTK_WIDGET(gtk_builder_get_object (builder, "dst_traveled_label"));

    gtk_widget_override_background_color(GTK_WIDGET(window), GTK_STATE_NORMAL, &color);
    
    pthread_mutex_init(&mutex_therm, NULL);
    pthread_mutex_init(&mutex_obd, NULL);
    pthread_mutex_init(&mutex_compass, NULL);
    pthread_create(&thread_therm, NULL, thermometer_thread, NULL);
    pthread_create(&thread_obd, NULL, obd_thread, NULL);
    pthread_create(&thread_compass, NULL, compass_thread, NULL);
    data = (struct update_data) {direction, time, temp, speed, a_speed, dst};
    g_timeout_add(100, update, (gpointer)&data);
    gtk_widget_show_all(window);
    gtk_main();

    pthread_mutex_destroy(&mutex_therm);
    pthread_mutex_destroy(&mutex_obd);
    pthread_mutex_destroy(&mutex_compass);


    return 0;
}

void *thermometer_thread(void *args){
    int ret;

    init_therm();

    while(run){
        pthread_mutex_lock(&mutex_therm);
        ret = get_temp(&temperature);
        if (ret) temperature = 0;
        pthread_mutex_unlock(&mutex_therm);

        if (ret) sleep(10);
        else sleep(5);
    }
    return NULL;
}

void *obd_thread(void *args){

    if (init_obd()){
        if (attempt_reconnect()) {
            return NULL;
        }
    }

    while(run){
        pthread_mutex_lock(&mutex_obd);
        if (get_speed(&current_speed)) {
            if (attempt_reconnect()) {
                break;
            } else {
                get_speed(&current_speed);
            }
        }
        get_average_speed(&average_speed, &current_speed);
        get_distance_traveled(&distance_traveled, &current_speed);
        pthread_mutex_unlock(&mutex_obd);
        usleep(33300);
    }
    system("sudo rfcomm unbind 0");
    return NULL;
}

void *compass_thread(void *args){
    init_mpu();

    while(run){
        pthread_mutex_lock(&mutex_compass);
        get_heading(curr_direction);
        pthread_mutex_unlock(&mutex_compass);
        sleep(1);
    }
    return NULL;
}

int update(gpointer labels){
    char temp[10] = {0}, temp1[10] = {0}, temp2[10] = {0};
    struct update_data *data = (struct update_data *) labels;
    FILE *fp;

    fp = popen("date +\"%-I:%M\"","r");
    fscanf(fp, "%[^\n]s", temp);
    pclose(fp);
    gtk_label_set_text(GTK_LABEL(data->time), temp);
    // printf("time: %s ", temp);
    memset(temp, 0, 10);


    pthread_mutex_lock(&mutex_therm);
    snprintf(temp, 10, "%d", temperature);
    pthread_mutex_unlock(&mutex_therm);
    gtk_label_set_text(GTK_LABEL(data->temp), temp);
    // printf("temp: %s ", temp);
    memset(temp, 0, 10);


    pthread_mutex_lock(&mutex_compass);
    gtk_label_set_text(GTK_LABEL(data->direction), curr_direction);
    // printf("direction: %s ", curr_direction);
    pthread_mutex_unlock(&mutex_compass);


    pthread_mutex_lock(&mutex_obd);
    snprintf(temp, 10, "%d", current_speed);
    snprintf(temp1, 10, "%d", (int) round(average_speed));
    snprintf(temp2, 10, "%d", (int) floor(distance_traveled));
    // printf("speed: %s\n", temp);
    pthread_mutex_unlock(&mutex_obd);
    gtk_label_set_text(GTK_LABEL(data->speed), temp);
    gtk_label_set_text(GTK_LABEL(data->a_speed), temp1);
    gtk_label_set_text(GTK_LABEL(data->dst), temp2);

    
    // static int number = 0;
    // number++;
    // if (number>100) {gtk_main_quit (); return FALSE;}
    return TRUE;
}
