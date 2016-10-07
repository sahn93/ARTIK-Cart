#!/usr/bin/python3

import sys
import math
import time
import RTIMU
import pprint
from config import CALIB_FILE, LOCATIONS, TXPOWER
from math import sqrt, pow, degrees
from subprocess import Popen, PIPE


def distance(rssi):
    return sqrt(pow(10, (TXPOWER - rssi) / 10))

"Initialize"

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

x, y = (0, 0)
yaws = []
s_prev = False
while True:
    time.sleep(t_interval)
    if imu.IMURead():
        data = imu.getIMUData()
        yaws.append(data['fusionPose'][2])
    with open('/sys/class/gpio/gpio%d/value' % pin, 'rb', 0) as f:
        s_curr = f.read() == b'0\n'
    if s_prev is not s_curr:
        s_prev = s_curr
        if not s_prev:
            yaw = sum(yaws)/len(yaws)
            yaws = []
            x += math.pi*diameter*math.cos(yaw)
            y += math.pi*diameter*math.sin(yaw)

sys.exit(0)

with Popen(['node', 'location.js'], stdout=PIPE) as scan:
    distances = {beacon: [] for beacon in LOCATIONS}
    while True:
        addr, rssi = scan.stdout.readline().split()
        addr = addr.decode()
        if addr in distances.keys():
            if len(distances[addr]) == 10:
                distances[addr].pop(0)
            distances[addr].append(int(rssi))
        if all(map(lambda x: len(x) == 10, distances.values())):
            foo = {x: distance(sum(distances[x])/10) for x in distances.keys()}
            print(foo)  # TODO
