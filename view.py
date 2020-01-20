import gps
import thermometer
import car
import time
import tkinter
import threading
import datetime
import math
import mpu9250

# Thermometer addresses
OUT_THERM_ADDR = '28-0315977942f6'

# Bluetooth address of ELM OBD dongle
ELM_ADDR = '00:1D:A5:00:48:7A'

# Globals
out_temp = '--'
direction = '--'
speed = 0
avg_speed = 0
dst_traveled = 0
quit = False
scale = 4.5
time_updated = False
bad_speed = True


def __out_temp_thread():
    global out_temp

    out_therm = thermometer.Thermometer(OUT_THERM_ADDR)
    out_temp = out_therm.get_temp()
    if out_temp == None:
        out_temp = 'er'
    while not quit:
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
    global time_updated

    g = gps.GPS()
    g.update_time()
    time_updated = True
    g.gps_thread.stop()

def __car_thread():
    global speed
    global avg_speed
    global dst_traveled
    global bad_speed

    c = car.Car(ELM_ADDR)
    while not quit:
        speed = round(c.get_speed())
        bad_speed = False
        avg_speed = round(c.get_average_speed())
        dst_traveled = math.floor(c.get_distance_traveled())
        time.sleep(.1)
    
    c.connection.stop()

def __mpu_thread():
    global direction
    global speed

    mpu = mpu9250.MPU9250()
    count = 0
    #mpu.calibrate()
    while not quit:
        if not (count % 100):
            direction = mpu.get_heading()
        time.sleep(0.010)
        count+=1

def __quit(e):
    global quit

    quit = True
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
car_thread = threading.Thread(target=__car_thread)

# start threads
out_therm_thread.start()
mpu_thread.start()
gps_thread.start()
car_thread.start()

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
