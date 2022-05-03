#include "car_display.h"

atomic_bool run = 1;
struct GuiLabels labels;
pthread_t thread_therm, thread_obd, thread_compass;

int main(int argc, char **argv){
    GtkWidget *window;
    GtkBuilder *builder;
    GtkCssProvider *cssProvider;
    GtkStyleContext *context;

    gtk_init(&argc, &argv);
    builder = gtk_builder_new();
    gtk_builder_add_from_file(builder, LAYOUT_FILE, NULL);

    window = GTK_WIDGET(gtk_builder_get_object (builder, "window"));

    labels = (struct GuiLabels) {
        GTK_WIDGET(gtk_builder_get_object(builder, "dir_label")),
        GTK_WIDGET(gtk_builder_get_object(builder, "clock_label")),
        GTK_WIDGET(gtk_builder_get_object(builder, "temp_label")),
        GTK_WIDGET(gtk_builder_get_object(builder, "speed_label")),
        GTK_WIDGET(gtk_builder_get_object(builder, "avg_speed_label")),
        GTK_WIDGET(gtk_builder_get_object(builder, "dst_traveled_label"))
    };

    cssProvider = gtk_css_provider_new();
    gtk_css_provider_load_from_data(cssProvider, "* { background-image:none; background-color:black;}",-1,NULL);
    context = gtk_widget_get_style_context(window); 
    gtk_style_context_add_provider(context, GTK_STYLE_PROVIDER(cssProvider),GTK_STYLE_PROVIDER_PRIORITY_USER);
    
    pthread_create(&thread_therm, NULL, thermometer_thread, NULL);
    pthread_create(&thread_obd, NULL, obd_thread, NULL);
    pthread_create(&thread_compass, NULL, compass_thread, NULL);

    g_signal_connect(window, "key_press_event", G_CALLBACK(check_escape), NULL);
    g_timeout_add(200, update_clock_gui, NULL);
    gtk_widget_show_all(window);
    gtk_main();

    return 0;
}

gboolean check_escape(GtkWidget *widget, GdkEventKey *event, gpointer data){
    if (event->keyval == GDK_KEY_Escape) {
        run = 0;
        pthread_join(thread_compass, NULL);
        pthread_join(thread_obd, NULL);
        pthread_join(thread_therm, NULL);

        gtk_main_quit();
        return TRUE;
    }
    return FALSE;
}

gboolean update_thermometer_gui(gpointer update_data){
    char temp[4] = {0};
    int *temperature = (int *) update_data;

    snprintf(temp, 4, "%d", *temperature);
    gtk_label_set_text(GTK_LABEL(labels.temp), temp);
    free(temperature);

    return G_SOURCE_REMOVE;
}

void *thermometer_thread(void *args){
    int ret, *temp;

    init_therm();

    while(run){
        temp = malloc(sizeof(int));
        ret = get_temp(temp);
        if (ret) {
            *temp = 0;
        }

        if (ret) {
            sleep(10);
        } else {
            sleep(5);
        }
        gdk_threads_add_idle(update_obd_gui, (gpointer *) temp);

    }
    return NULL;
}

gboolean update_obd_gui(gpointer update_data){
    struct ObdData *data = (struct ObdData *) update_data;
    char temp[4] = {0};

    snprintf(temp, 4, "%d", data->speed);
    gtk_label_set_text(GTK_LABEL(labels.speed), temp);
    memset(temp, 0, 4);

    snprintf(temp, 4, "%d", (int) round(data->avg_speed));
    gtk_label_set_text(GTK_LABEL(labels.a_speed), temp);
    memset(temp, 0, 4);

    snprintf(temp, 4, "%d", (int) floor(data->dst));
    gtk_label_set_text(GTK_LABEL(labels.dst), temp);

    free(data);

    return G_SOURCE_REMOVE;
}

void *obd_thread(void *args){
    struct ObdData *data;
    double prev_avg = 0;

    if (init_obd()){
        if (attempt_reconnect()) {
            return NULL;
        }
    }

    while(run){
        data = (struct ObdData *) malloc(sizeof(struct ObdData));
        if (get_speed(&data->speed)) {
            if (attempt_reconnect()) {
                break;
            } else {
                get_speed(&data->speed);
            }
        }
        data->avg_speed = prev_avg;
        get_average_speed(&data->avg_speed, &data->speed);
        get_distance_traveled(&data->dst, &data->avg_speed);
        prev_avg = data->avg_speed;
        gdk_threads_add_idle(update_obd_gui, (gpointer *) data);
        usleep(33300);
    }
    system("sudo rfcomm unbind 0");
    return NULL;
}

gboolean update_compass_gui(gpointer update_data){
    char *direction = (char *) update_data;

    gtk_label_set_text(GTK_LABEL(labels.direction), direction);
    free(direction);

    return G_SOURCE_REMOVE;
}

void *compass_thread(void *args){
    char *direction;
    init_mpu();

    while(run){
        direction = calloc(3,1);
        
        get_heading(direction);
        gdk_threads_add_idle(update_compass_gui, (gpointer *) direction);
        sleep(1);
    }
    return NULL;
}

gboolean update_clock_gui(gpointer update_data){
    char temp[6] = {0};
    FILE *fp;

    fp = popen("date +\"%-I:%M\"","r");
    fscanf(fp, "%[^\n]s", temp);
    pclose(fp);
    gtk_label_set_text(GTK_LABEL(labels.time), temp);

    return G_SOURCE_CONTINUE;
}
