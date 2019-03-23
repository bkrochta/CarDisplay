import mpu9250
import gps
import thermometer
import subprocess
import math
import time as tim
from tkinter import *

g = gps.GPS()
m = mpu9250.MPU9250()
#m.calibrate()

root = Tk()
root.attributes("-fullscreen", True)
root.configure(background='black')

Button(root, text="Quit", command=root.destroy).pack()

clock = Label(root, font=('arial',500, 'bold'), fg='red', bg='black')
clock.pack()

direction = Label(root, font=('arial',100, 'bold'), fg='red', bg='black')
direction.pack()

temp_in = Label(root, font=('arial',25, 'bold'), fg='red', bg='black')
temp_in.pack()

temp_out = Label(root, font=('arial',25, 'bold'), fg='red', bg='black')
temp_out.pack()

def tick():
    process = subprocess.run('date', stdout=subprocess.PIPE)
    time = str(process.stdout).split(':')
    hours = int(time[0][-2:])
    mins = time[1]
    secs = time[2][:-2]
    if hours >= 12:
        hours -=12
        pm = True
    else:
        pm = False
    if hours == 0:
        hours = 12

    time = str(hours) + ':' + mins
    if pm:
        time += ' pm'
    else:
        time += ' am'

    mag = m.read()
    h = m.get_heading(math.atan2(mag[1],mag[0])*(180/math.pi))

    direction.config(text=h)
    clock.config(text=time)
    temp_in.config(text='NA')
    temp_out.config(text='NA')
    tim.sleep(.25)
    # calls itself every 200 milliseconds
    # to update the time display as needed
    # could use &gt;200 ms, but display gets jerky
    clock.after(20, tick)

tick()
root.mainloop()
