import gps
import thermometer
import time
import tkinter
import threading
import datetime
import math
import mpu9250

# Thermometer addresses
OUT_THERM_ADDR = '28-0315977942f6'

# Globals
out_temp = '--'
direction = '--'
speed = 0
avg_speed = 0
dst_traveled = 0
quit = 0
scale = 4.5
time_updated = False
bad_speed = True


def __out_temp_thread():
    global out_temp

    out_therm = thermometer.Thermometer(OUT_THERM_ADDR)
    out_temp = out_therm.get_temp()
    if out_temp == None:
        out_temp = 'er'
    while quit == 0:
        if not bad_speed:
            while speed < 10:
                while speed < 10:
                    time.sleep(2)
                time.sleep(60)
        out_temp = out_therm.get_temp()
        if out_temp == None:
            out_temp = 'er'
        time.sleep(5)


def __gps_thread():
    global speed
    global avg_speed
    global dst_traveled
    global time_updated
    global bad_speed

    g = gps.GPS()
    g.update_time()
    time_updated = True
    while quit == 0:
        s = g.get_speed()
        if s != None:
            speed = math.floor(s)
            bad_speed = False
        else:
            bad_speed = True
        # direction = g.get_heading()
        # if direction == None:
        #     direction = '--'
        avg_speed = int(g.get_average_speed())
        dst_traveled = math.floor(g.get_distance_traveled())
        time.sleep(1)


def __mpu_thread():
    global direction
    global speed

    mpu = mpu9250.MPU9250()
    count = 0
    #mpu.calibrate()
    while quit == 0:
        if not (count % 100):
            direction = mpu.get_heading()
        if not bad_speed:
            accel = mpu.read_accel()
            #print(x)
            speed = speed + (accel[1] * .01 *9.8*2.237)
        time.sleep(0.010)
        count+=1

def __quit(e):
    global quit

    quit = 1
    root.destroy()


root = tkinter.Tk()
root.attributes("-fullscreen", True)
#root.geometry("1200x800")
root.configure(background='black')
root.bind("<Escape>", __quit)

# Create data labels
clock_label = tkinter.Label(root, font=('arial',int(300/scale), 'bold'), fg='red', bg='black', anchor='n')
dir_label = tkinter.Label(root, font=('arial',int(200/scale), 'bold'), fg='red', bg='black', anchor='n')
temp_out_label = tkinter.Label(root, font=('arial',int(200/scale), 'bold'), fg='red', bg='black', anchor='ne')
speed_label = tkinter.Label(root, font=('arial',int(800/scale), 'bold'), fg='red', bg='black')
avg_speed_label = tkinter.Label(root, font=('arial',int(200/scale), 'bold'), fg='red', bg='black', anchor='s')
dst_traveled_label = tkinter.Label(root, font=('arial',int(200/scale), 'bold'), fg='red', bg='black', anchor='s')

# Create unit and description labels
out_f_label = tkinter.Label(root, font=('arial',int(100/scale), 'bold'), fg='red', bg='black', text='\u00b0F', anchor='ne')
mph_label1 = tkinter.Label(root, font=('arial',int(100/scale), 'bold'), fg='red', bg='black', text='mph')
mph_label2 = tkinter.Label(root, font=('arial',int(50/scale), 'bold'), fg='red', bg='black', text='mph', anchor='w')
miles_label = tkinter.Label(root, font=('arial',int(50/scale), 'bold'), fg='red', bg='black', text='miles')
as_label = tkinter.Label(root, font=('arial',int(50/scale), 'bold'), fg='red', bg='black', text='Avg Speed:', anchor='w')
dt_label = tkinter.Label(root, font=('arial',int(50/scale), 'bold'), fg='red', bg='black', text='Dst Traveled:')

# Place data labels
clock_label.place(relx=0.29, rely=0, relheight=0.21, relwidth=0.42)
dir_label.place(relx=0, rely=0, relheight=0.2, relwidth=0.2)
temp_out_label.place(relx=0.775, rely=0, relheight=0.2, relwidth=0.175)
speed_label.place(relx=0.2, rely=0.21, relheight=0.58, relwidth=0.6)
avg_speed_label.place(relx=0, rely=0.8, relheight=0.2, relwidth=0.15)
dst_traveled_label.place(relx=0.2, rely=0.8, relheight=0.2, relwidth=0.2)

# Place unit and description labels
out_f_label.place(relx=0.94, rely=0.02, relheight=0.1, relwidth=0.06)
#mph_label1.place(relx=0.7, rely=0.625, relheight=0.1, relwidth=0.150)
mph_label2.place(relx=0.14, rely=0.925, relheight=0.05, relwidth=0.06)
miles_label.place(relx=0.38, rely=0.925, relheight=0.05, relwidth=0.075)
as_label.place(relx=0.0, rely=0.79, relheight=0.05, relwidth=0.14)
dt_label.place(relx=0.2, rely=0.79, relheight=0.05, relwidth=0.16)

# Debugging quit button
#tkinter.Button(root, text="Quit", command=lambda: __quit(None)).place(relx=0.8, rely=0.5, relheight=0.2, relwidth=0.2)

# create threads for sensors
out_therm_thread = threading.Thread(target=__out_temp_thread)
mpu_thread = threading.Thread(target=__mpu_thread)
gps_thread = threading.Thread(target=__gps_thread)

# start threads
out_therm_thread.start()
mpu_thread.start()
gps_thread.start()

# MAIN LOOP #
while True:
    dir_label.config(text=direction)
    if time_updated:
        clock_label.config(text=datetime.datetime.now().strftime('%-I:%M'))
    temp_out_label.config(text=out_temp)
    speed_label.config(text=speed)
    avg_speed_label.config(text=avg_speed)
    dst_traveled_label.config(text=dst_traveled)

    root.update_idletasks()
    root.update()
    time.sleep(0.100)
