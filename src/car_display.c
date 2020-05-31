#include "car_display.h"

pthread_mutex_t mutex_therm, mutex_obd, mutex_compass;
int run=1, temperature, current_speed, average_speed, distance_traveled;
char curr_direction[3];

int main(int argc, char **argv){
    GtkWidget *window, *grid, *grid_temp, *grid_top, *grid_bot, *grid_speed, *grid_a_speed, *grid_dst, *direction, *time, *temp, *temp_unit, 
            *speed, *speed_unit, *a_speed_l, *dst_l, * a_speed, *a_speed_u, *dst, *dst_u;
    char *speed_font, *speed_unit_font, *temp_font, *temp_unit_font, *time_font, *direction_font, *a_speed_l_font, *a_speed_font, *a_speed_u_font, *dst_l_font, *dst_font, *dst_u_font;
    pthread_t thread_therm, thread_obd, thread_compass;
    struct update_data data;
    GdkRGBA color = {0,0,0,1};
    
    gtk_init(&argc, &argv);

    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);

    gtk_window_set_decorated(GTK_WINDOW(window), FALSE);
    gtk_window_set_position(GTK_WINDOW(window), GTK_WIN_POS_CENTER);
    gtk_window_set_default_size(GTK_WINDOW(window), 656, 416);
    gtk_window_set_resizable(GTK_WINDOW(window), FALSE);
    
    //base font

    grid = gtk_grid_new();
    //gtk_grid_set_row_homogeneous(GTK_GRID(grid), TRUE);
    gtk_container_add(GTK_CONTAINER(window), grid);
    gtk_widget_override_background_color(GTK_WIDGET(window), GTK_STATE_NORMAL, &color);
    
    grid_top = gtk_grid_new();
    gtk_grid_attach(GTK_GRID(grid), grid_top, 0, 0, 1, 1);
    //gtk_grid_set_column_homogeneous(GTK_GRID(grid_top), TRUE);
    gtk_widget_set_valign (grid_top, GTK_ALIGN_START);
    gtk_widget_set_vexpand (grid_top, TRUE);
    // gtk_widget_set_hexpand (grid_top, TRUE);


    grid_temp = gtk_grid_new();
    gtk_widget_set_halign (grid_temp, GTK_ALIGN_END);
    gtk_widget_set_valign (grid_temp, GTK_ALIGN_START);
    gtk_grid_attach(GTK_GRID(grid_top), grid_temp, 2, 0, 1, 1);
    

    temp = gtk_label_new(NULL);
    temp_font = g_strdup_printf("<span font=\"40\" color=\"red\">"
                               "<b>--</b>"
                             "</span>");
    gtk_label_set_markup(GTK_LABEL(temp), temp_font);
    free(temp_font);
    gtk_widget_set_halign (temp, GTK_ALIGN_START);
    gtk_widget_set_valign (temp, GTK_ALIGN_START);
    gtk_grid_attach(GTK_GRID(grid_temp), temp, 0, 0, 1, 1);

    temp_unit = gtk_label_new(NULL);
    temp_unit_font = g_strdup_printf("<span font=\"25\" color=\"red\">"
                               "<b>\u00b0F</b>"
                             "</span>");
    gtk_label_set_markup(GTK_LABEL(temp_unit), temp_unit_font);
    free(temp_unit_font);
    gtk_widget_set_halign (temp_unit, GTK_ALIGN_END);
    gtk_widget_set_valign (temp_unit, GTK_ALIGN_START);
    gtk_grid_attach_next_to(GTK_GRID(grid_temp), temp_unit, temp, GTK_POS_RIGHT, 1, 1);
    
    direction = gtk_label_new(NULL);
    direction_font = g_strdup_printf("<span font=\"40\" color=\"red\">"
                               "<b>--</b>"
                             "</span>");
    gtk_label_set_markup(GTK_LABEL(direction), direction_font);
    free(direction_font);
    gtk_widget_set_halign (direction, GTK_ALIGN_START);
    gtk_widget_set_valign (direction, GTK_ALIGN_START);
    gtk_grid_attach(GTK_GRID(grid_top), direction, 0, 0, 1, 1);

    time = gtk_label_new(NULL);
    time_font = g_strdup_printf("<span font=\"70\" color=\"red\">"
                               "<b>00:00</b>"
                             "</span>");
    gtk_label_set_markup(GTK_LABEL(time), time_font);
    free(time_font);
    gtk_widget_set_halign (time, GTK_ALIGN_CENTER);
    gtk_widget_set_valign (time, GTK_ALIGN_START);
    gtk_widget_set_hexpand (time, TRUE);
    gtk_grid_attach(GTK_GRID(grid_top), time, 1, 0, 1, 1);


    grid_speed = gtk_grid_new();
    gtk_widget_set_halign (grid_speed, GTK_ALIGN_CENTER);
    gtk_widget_set_valign (grid_speed, GTK_ALIGN_CENTER);
     gtk_widget_set_vexpand (grid_speed, TRUE);
     gtk_widget_set_hexpand (grid_speed, FALSE);
    gtk_grid_attach(GTK_GRID(grid), grid_speed, 0, 1, 1, 1);


    speed = gtk_label_new(NULL);
    speed_font = g_strdup_printf("<span font=\"120\" color=\"red\" background=\"black\">"
                               "<b>0</b>"
                             "</span>");
    gtk_label_set_markup(GTK_LABEL(speed), speed_font);
    free(speed_font);
    gtk_widget_set_halign (speed, GTK_ALIGN_CENTER);
    gtk_widget_set_valign (speed, GTK_ALIGN_CENTER);
    //gtk_widget_set_vexpand(speed,TRUE);
    gtk_grid_attach(GTK_GRID(grid_speed), speed, 0, 1, 1, 1);

    speed_unit = gtk_label_new(NULL);
    speed_unit_font = g_strdup_printf("<span font=\"12\" color=\"red\">"
                               "<b>   mph</b>"
                             "</span>");
    gtk_label_set_markup(GTK_LABEL(speed_unit), speed_unit_font);
    free(speed_unit_font);
    gtk_widget_set_halign (speed_unit, GTK_ALIGN_CENTER);
    gtk_widget_set_valign (speed_unit, GTK_ALIGN_END);
    gtk_grid_attach_next_to(GTK_GRID(grid_speed), speed_unit, speed, GTK_POS_RIGHT, 1, 1);


    grid_bot = gtk_grid_new();
    gtk_widget_set_halign (grid_bot, GTK_ALIGN_START);
    //gtk_widget_set_valign (grid_bot, GTK_ALIGN_END);
    gtk_widget_set_vexpand (grid_bot, TRUE);
    // gtk_widget_set_hexpand (grid_bot, TRUE);
    gtk_grid_attach(GTK_GRID(grid), grid_bot, 0, 2, 1, 1);

    grid_a_speed = gtk_grid_new();
    gtk_widget_set_halign (grid_a_speed, GTK_ALIGN_START);
    gtk_widget_set_valign (grid_a_speed, GTK_ALIGN_END);
    gtk_grid_attach(GTK_GRID(grid_bot), grid_a_speed, 0, 0, 1, 1);

    a_speed_l = gtk_label_new(NULL);
    a_speed_l_font = g_strdup_printf("<span font=\"12\" color=\"red\">"
                               "<b>Avg Speed:</b>"
                             "</span>");
    gtk_label_set_markup(GTK_LABEL(a_speed_l), a_speed_l_font);
    free(a_speed_l_font);
    gtk_grid_attach(GTK_GRID(grid_a_speed), a_speed_l, 0, 0, 2, 1);

    a_speed = gtk_label_new(NULL);
    a_speed_font = g_strdup_printf("<span font=\"40\" color=\"red\">"
                               "<b>0</b>"
                             "</span>");
    gtk_label_set_markup(GTK_LABEL(a_speed), a_speed_font);
    free(a_speed_font);
    gtk_widget_set_halign (a_speed, GTK_ALIGN_START);
    gtk_widget_set_valign (a_speed, GTK_ALIGN_END);
    gtk_grid_attach(GTK_GRID(grid_a_speed), a_speed, 0, 1, 1, 1);

    a_speed_u = gtk_label_new(NULL);
    a_speed_u_font = g_strdup_printf("<span font=\"12\" color=\"red\">"
                               "<b>mph</b>"
                             "</span>");
    gtk_label_set_markup(GTK_LABEL(a_speed_u), a_speed_u_font);
    free(a_speed_u_font);
    gtk_widget_set_halign (a_speed_u, GTK_ALIGN_START);
    gtk_widget_set_valign (a_speed_u, GTK_ALIGN_END);
    gtk_grid_attach_next_to(GTK_GRID(grid_a_speed), a_speed_u, a_speed, GTK_POS_RIGHT, 1, 1);

    grid_dst = gtk_grid_new();
    gtk_widget_set_halign (grid_dst, GTK_ALIGN_START);
    gtk_widget_set_valign (grid_dst, GTK_ALIGN_END);
    gtk_grid_attach(GTK_GRID(grid_bot), grid_dst, 1, 0, 1, 1);

    dst_l = gtk_label_new(NULL);
    dst_l_font = g_strdup_printf("<span font=\"12\" color=\"red\">"
                               "<b>Dst Traveled:</b>"
                             "</span>");
    gtk_label_set_markup(GTK_LABEL(dst_l), dst_l_font);
    free(dst_l_font);
    gtk_grid_attach(GTK_GRID(grid_dst), dst_l, 0, 0, 2, 1);

    dst = gtk_label_new(NULL);
    dst_font = g_strdup_printf("<span font=\"40\" color=\"red\">"
                               "<b>0</b>"
                             "</span>");
    gtk_label_set_markup(GTK_LABEL(dst), dst_font);
    free(dst_font);
    gtk_widget_set_halign (dst, GTK_ALIGN_START);
    gtk_widget_set_valign (dst, GTK_ALIGN_END);
    gtk_grid_attach(GTK_GRID(grid_dst), dst, 0, 1, 1, 1);

    dst_u = gtk_label_new("miles");
    dst_u = gtk_label_new(NULL);
    dst_u_font = g_strdup_printf("<span font=\"12\" color=\"red\">"
                               "<b>miles</b>"
                             "</span>");
    gtk_label_set_markup(GTK_LABEL(dst_u), dst_u_font);
    free(dst_u_font);
    gtk_widget_set_halign (dst_u, GTK_ALIGN_START);
    gtk_widget_set_valign (dst_u, GTK_ALIGN_END);
    gtk_grid_attach_next_to(GTK_GRID(grid_dst), dst_u, dst, GTK_POS_RIGHT, 1, 1);
    
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
    init_therm();

    while(run){
        pthread_mutex_lock(&mutex_therm);
        temperature = get_temp();
        pthread_mutex_unlock(&mutex_therm);
        sleep(5);
    }
    return NULL;
}

void *obd_thread(void *args){
    int ret, timeout = 0;

    ret = init_obd();
    while(ret && timeout < 5){
        sleep(2);
        ret = init_obd();
        timeout++;
    }

    while(run){
        timout = 0;
        pthread_mutex_lock(&mutex_obd);
        ret = get_speed(&current_speed);
        while(ret && timeout < 5){
            sleep(1);
            ret = get_speed(&current_speed);
            timeout++;
        }
        get_average_speed(&average_speed, &current_speed);
        get_distance_traveled(&distance_traveled, &current_speed);
        pthread_mutex_unlock(&mutex_obd);
        sleep(.1);
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
    char *font, *font1, *font2, time[10] = {0};
    struct update_data *data = (struct update_data *) labels;
    FILE *fp;

    fp = popen("date +\"%-I:%M\"","r");
    fscanf(fp, "%[^\n]s", time);
    pclose(fp);

    font = g_strdup_printf("<span font=\"70\" color=\"red\">"
                               "<b>%s</b>"
                             "</span>", time);
    gtk_label_set_markup(GTK_LABEL(data->time), font);
    free(font);

    pthread_mutex_lock(&mutex_therm);
    font = g_strdup_printf("<span font=\"40\" color=\"red\">"
                               "<b>%d</b>"
                             "</span>", temperature);
    pthread_mutex_unlock(&mutex_therm);
    gtk_label_set_markup(GTK_LABEL(data->temp), font);
    free(font);

    pthread_mutex_lock(&mutex_compass);
    font = g_strdup_printf("<span font=\"40\" color=\"red\">"
                               "<b>%s</b>"
                             "</span>", curr_direction);
    pthread_mutex_unlock(&mutex_compass);
    gtk_label_set_markup(GTK_LABEL(data->direction), font);
    free(font);

    pthread_mutex_lock(&mutex_obd);
    font = g_strdup_printf("<span font=\"120\" color=\"red\" >"
                               "<b>%d</b>"
                             "</span>", current_speed);
    font1 = g_strdup_printf("<span font=\"40\" color=\"red\">"
                               "<b>%d</b>"
                             "</span>", average_speed);
    font2 = g_strdup_printf("<span font=\"40\" color=\"red\">"
                               "<b>%d</b>"
                             "</span>", distance_traveled);
    pthread_mutex_unlock(&mutex_obd);
    gtk_label_set_markup(GTK_LABEL(data->speed), font);
    gtk_label_set_markup(GTK_LABEL(data->a_speed), font1);
    gtk_label_set_markup(GTK_LABEL(data->dst), font2);
    free(font);
    free(font1);
    free(font2);
    
    return TRUE;
}
