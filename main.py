#!/usr/bin/python3

import os
import sys
import math
import time
import RTIMU
import signal
from config import CALIB_FILE, LOCATIONS, TXPOWER
from math import pi, sqrt, pow, degrees


def distance(rssi):
    return sqrt(pow(10, (TXPOWER - rssi) / 10))

s = RTIMU.Settings(CALIB_FILE)
imu = RTIMU.RTIMU(s)
if (not imu.IMUInit()):
    print('IMU Init Failed')
    sys.exit(1)
else:
    print('IMU Init Succeeded: ' + imu.IMUName())
imu.setSlerpPower(0.02)
imu.setGyroEnable(True)
imu.setAccelEnable(True)
imu.setCompassEnable(True)
t_interval = imu.IMUGetPollInterval()/1000.0

diameter = 3.4
pin = 18
if os.path.exists('/sys/class/gpio/gpio%d/direction' % pin):
    with open('/sys/class/gpio/unexport', 'w') as f:
        f.write(str(pin))
with open('/sys/class/gpio/export', 'w') as f:
    f.write(str(pin))
with open('/sys/class/gpio/gpio%d/direction' % pin, 'w') as f:
    f.write('in')

(x, y, w_prev, theta_prev, theta_curr) = (0, 0, 0, 0, 0)
s_prev = False
dt = 0.01
with open('./coordinates.csv', 'w') as ff:
    ff.write("x(cm), y(cm), time_interval(s)\n")
    tstart = time.time()
    while True:
        time.sleep(t_interval)
        if imu.IMURead():
            data = imu.getIMUData()
            w_curr = data['gyro'][2]
            theta_curr += 0.5*dt*(w_prev + w_curr)
            w_prev = w_curr
        with open('/sys/class/gpio/gpio%d/value' % pin, 'rb', 0) as f:
            s_curr = f.read() == b'0\n'
        if s_prev is not s_curr:
            s_prev = s_curr
            if not s_prev:
                theta = 0.5*(theta_prev + theta_curr)
                x += pi*diameter*math.cos(theta)
                y += pi*diameter*math.sin(theta)
                theta_prev = theta_curr
                print("%.1fcm, %.1fcm, %.1fs" % (x, y, time.time() - tstart))
                ff.write("%.1f, %.1f, %.1f\n" % (x, y, time.time() - tstart))
                tstart = time.time();
