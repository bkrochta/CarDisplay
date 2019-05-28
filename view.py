import mpu9250
import gps
import thermometer
import time
import tkinter
import threading

# Thermometer addresses
IN_THERM_ADDR = '28-031597799b7d'
OUT_THERM_ADDR = '28-0315977942f6'

# Globals
ct = 0
in_temp = 0
out_temp = 0
direction = 0
speed = 0
quit = 0
scale = 4.5

def __in_temp_thread():
    global in_temp

    in_therm = thermometer.Thermometer(IN_THERM_ADDR)
    while quit == 0:
        in_temp = in_therm.get_temp()


def __out_temp_thread():
    global out_temp

    out_therm = thermometer.Thermometer(OUT_THERM_ADDR)
    while quit == 0:
        out_temp = out_therm.get_temp()


def __gps_thread():
    global speed

    g = gps.GPS()
    while quit == 0:
        g.update()
        speed = g.get_speed()


def __mpu_thread():
    global direction

    mpu = mpu9250.MPU9250()
    #mpu.calibrate()
    while quit == 0:
        direction = mpu.get_heading()

def __quit():
    quit = 1
    root.detroy()


root = tkinter.Tk()
root.attributes("-fullscreen", True)
root.configure(background='black')

clock_label = tkinter.Label(root, font=('arial',100/scale, 'bold'), fg='red', bg='black')
dir_label = tkinter.Label(root, font=('arial',100/scale, 'bold'), fg='red', bg='black')
temp_in_label = tkinter.Label(root, font=('arial',100/scale, 'bold'), fg='red', bg='black')
temp_out_label = tkinter.Label(root, font=('arial',100/scale, 'bold'), fg='red', bg='black')
speed_label = tkinter.Label(root, font=('arial',400/scale, 'bold'), fg='red', bg='black')

clock_label.place(relx=0.2, rely=0, relheight=0.2, relwidth=0.6)
dir_label.place(relx=0, rely=0, relheight=0.2, relwidth=0.2)
temp_in_label.place(relx=0, rely=0.8, relheight=0.2, relwidth=0.2)
temp_out_label.place(relx=0.8, rely=0, relheight=0.2, relwidth=0.2)
speed_label.place(relx=0.3, rely=0.3, relheight=0.6, relwidth=0.6)

tkinter.Button(root, text="Quit", command=__quit).place(relx=0.8, rely=0.5, relheight=0.2, relwidth=0.2)

in_therm_thread = threading.Thread(task=__in_temp_thread)
out_therm_thread = threading.Thread(task=__out_temp_thread)
mpu_thread = threading.Thread(task=__mpu_thread)
gps_thread = threading.Thread(task=__gps_thread)

in_therm_thread.start()
# out_therm_thread.start()
mpu_thread.start()
gps_thread.start()




def tick():
    global ct

    dir_label.config(text=direction)
    clock_label.config(text=clock)
    temp_in_label.config(text=in__therm)
    temp_out_label.config(text=ct)
    ct += 1
    # calls itself every 200 milliseconds
    # to update the time display as needed
    # could use &gt;200 ms, but display gets jerky
    clock.after(200, tick)

tick()
root.mainloop()
