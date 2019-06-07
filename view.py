import mpu9250
import gps
import thermometer
import time
import tkinter
import threading
import datetime
import math

# Thermometer addresses
IN_THERM_ADDR = '28-031597799b7d'
OUT_THERM_ADDR = '28-0315977942f6'

# Globals
in_temp = '--'
out_temp = '--'
direction = '--'
speed = '--'
avg_speed = 20
dst_traveled = 500
quit = 0
scale = 4.5

def __in_temp_thread():
    global in_temp

    in_therm = thermometer.Thermometer(IN_THERM_ADDR)
    while quit == 0:
        in_temp = in_therm.get_temp()
        if in_temp == None:
            in_temp = 'er'


def __out_temp_thread():
    global out_temp

    out_therm = thermometer.Thermometer(OUT_THERM_ADDR)
    while quit == 0:
        out_temp = out_therm.get_temp()
        if out_temp == None:
            out_temp = 'er'
        while speed < 5:
            time.sleep(10)


def __gps_thread():
    global speed
    global avg_speed
    global dst_traveled

    g = gps.GPS()
    g.update_time()
    while quit == 0:
        g.update()
        speed = math.floor(g.get_speed())
        direction = g.get_heading()
        if direction == None:
            direction = '--'
        # avg_speed = int(g.get_average_speed())
        # dst_traveled = int(g.get_distance_traveled())
        time.sleep(0.100)


def __mpu_thread():
    global direction

    mpu = mpu9250.MPU9250()
    #mpu.calibrate()
    while quit == 0:
        direction = mpu.get_heading()
        time.sleep(0.100)

def __quit(e):
    global quit

    quit = 1
    root.destroy()


root = tkinter.Tk()
root.attributes("-fullscreen", True)
root.configure(background='black')
root.bind("<Escape>", __quit)

# Create data labels
clock_label = tkinter.Label(root, font=('arial',int(300/scale), 'bold'), fg='red', bg='black')
dir_label = tkinter.Label(root, font=('arial',int(200/scale), 'bold'), fg='red', bg='black')
temp_in_label = tkinter.Label(root, font=('arial',int(200/scale), 'bold'), fg='red', bg='black')
temp_out_label = tkinter.Label(root, font=('arial',int(200/scale), 'bold'), fg='red', bg='black')
speed_label = tkinter.Label(root, font=('arial',int(800/scale), 'bold'), fg='red', bg='black')
# avg_speed_label = tkinter.Label(root, font=('arial',int(200/scale), 'bold'), fg='red', bg='black')
# dst_traveled_label = tkinter.Label(root, font=('arial',int(200/scale), 'bold'), fg='red', bg='black')

# Create unit and description labels
in_label = tkinter.Label(root, font=('arial',int(100/scale), 'bold'), fg='red', bg='black', text='in:')
# mph_label1 = tkinter.Label(root, font=('arial',int(100/scale), 'bold'), fg='red', bg='black', text='mph')
# mph_label2 = tkinter.Label(root, font=('arial',int(50/scale), 'bold'), fg='red', bg='black', text='mph')
# miles_label = tkinter.Label(root, font=('arial',int(50/scale), 'bold'), fg='red', bg='black', text='miles')
# as_label = tkinter.Label(root, font=('arial',int(100/scale), 'bold'), fg='red', bg='black', text='avg speed:')
# dt_label = tkinter.Label(root, font=('arial',int(100/scale), 'bold'), fg='red', bg='black', text='dst traveled:')

# Place data labels
clock_label.place(relx=0.225, rely=0, relheight=0.2, relwidth=0.55)
dir_label.place(relx=0, rely=0, relheight=0.2, relwidth=0.225)
temp_in_label.place(relx=0, rely=0.8, relheight=0.2, relwidth=0.225)
temp_out_label.place(relx=0.775, rely=0, relheight=0.2, relwidth=0.225)
speed_label.place(relx=0.2, rely=0.2, relheight=0.6, relwidth=0.6)
# avg_speed_label.place(relx=0.2, rely=0.8, relheight=0.2, relwidth=0.2)
# dst_traveled_label.place(relx=0.4, rely=0.8, relheight=0.2, relwidth=0.2)

# Place unit and description labels
in_label.place(relx=0.0, rely=0.775, relheight=0.05, relwidth=0.075)
# mph_label1.place(relx=0.8, rely=0.7, relheight=0.05, relwidth=0.075)
# mph_label2.place(relx=0.4, rely=0.9, relheight=0.05, relwidth=0.075)
# miles_label.place(relx=0.6, rely=0.9, relheight=0.05, relwidth=0.075)
# as_label.place(relx=0.2, rely=0.775, relheight=0.05, relwidth=0.075)
# dt_label.place(relx=0.4, rely=0.775, relheight=0.05, relwidth=0.075)

# Debugging quit button
#tkinter.Button(root, text="Quit", command=lambda: __quit(None)).place(relx=0.8, rely=0.5, relheight=0.2, relwidth=0.2)

# create threads for sensors
in_therm_thread = threading.Thread(target=__in_temp_thread)
out_therm_thread = threading.Thread(target=__out_temp_thread)
#mpu_thread = threading.Thread(target=__mpu_thread)
gps_thread = threading.Thread(target=__gps_thread)

# start threads
in_therm_thread.start()
out_therm_thread.start()
#mpu_thread.start()
gps_thread.start()

# MAIN LOOP #
while True:
    dir_label.config(text=direction)
    if speed != '--':
        clock_label.config(text=datetime.datetime.now().strftime('%-I:%M'))
    temp_in_label.config(text=str(in_temp) + '\u00b0F')
    temp_out_label.config(text=str(out_temp) + '\u00b0F')
    speed_label.config(text=speed)
    # avg_speed_label.config(text=avg_speed)
    # dst_traveled_label.config(text=dst_traveled)

    root.update_idletasks()
    root.update()
    time.sleep(0.200)
