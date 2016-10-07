#!/usr/bin/python3

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
with open('/sys/class/gpio/export', 'w') as f:
    f.write(str(pin))
with open('/sys/class/gpio/gpio%d/direction' % pin, 'w') as f:
    f.write('in')

def safe_exit(signal=None, frame=None):
    print('GOOD BYE!')
    with open('/sys/class/gpio/unexport', 'w') as f:
        f.write(str(pin))
    sys.exit(0)
signal.signal(signal.SIGTERM, safe_exit)
signal.signal(signal.SIGINT, safe_exit)

x, y = (0, 0)
yaw = None
s_prev = False
while True:
    time.sleep(t_interval)
    if imu.IMURead():
        data = imu.getIMUData()
        yaw = data['fusionPose'][2]
    with open('/sys/class/gpio/gpio%d/value' % pin, 'rb', 0) as f:
        s_curr = f.read() == b'0\n'
    if s_prev is not s_curr:
        s_prev = s_curr
        if not s_prev:
            x += pi*diameter*math.cos(yaw)
            y += pi*diameter*math.sin(yaw)
