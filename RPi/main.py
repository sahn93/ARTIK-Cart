#!/usr/bin/python3
import os
import sys
import time
import pickle
import RTIMU
import serial

# check admin rights

if os.getuid() != 0:
    print('You are not root :(')
    sys.exit(1)


# initialize gyroscope

s = RTIMU.Settings("config.ini")
imu = RTIMU.RTIMU(s)
if (not imu.IMUInit()):
    print('IMU Init Failed')
    sys.exit(1)
else:
    print('IMU Init Succeeded: ' + imu.IMUName())
imu.setGyroEnable(True)
imu.setAccelEnable(False)
imu.setCompassEnable(False)
t_interval = imu.IMUGetPollInterval()/1000.0


# initialize serial port

tty = serial.Serial('/dev/ttyAMA0')


# main loop: read sensor and send through uart

while True:
    time.sleep(t_interval)
    while imu.IMURead():
        data = imu.getIMUData()
        w_curr = data['gyro'][2]
        tty.write(pickle.dumps(w_curr))
        tty.write(b'\n')
