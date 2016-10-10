#!/usr/bin/python3
import os
import sys
import math
import time
import RTIMU
import socket
import signal
import pickle
import subprocess as sp
import multiprocessing as mp
from config import CALIB_FILE, LOCATIONS, TXPOWER
from math import pi, sqrt, pow, degrees, cos, sin


# check admin rights

if os.getuid() != 0:
    print('You are not root :(')
    sys.exit(1)


# initialize gyroscope

s = RTIMU.Settings(CALIB_FILE)
imu = RTIMU.RTIMU(s)
if (not imu.IMUInit()):
    print('IMU Init Failed')
    sys.exit(1)
else:
    print('IMU Init Succeeded: ' + imu.IMUName())
#imu.setSlerpPower(0.02)
imu.setGyroEnable(True)
imu.setAccelEnable(False)
imu.setCompassEnable(False)
t_interval = imu.IMUGetPollInterval()/1000.0


# initialize light sensor

diameter = 3.4
pin = 12
if os.path.exists('/sys/class/gpio/gpio%d/direction' % pin):
    with open('/sys/class/gpio/unexport', 'w') as f:
        f.write(str(pin))
with open('/sys/class/gpio/export', 'w') as f:
    f.write(str(pin))
with open('/sys/class/gpio/gpio%d/direction' % pin, 'w') as f:
    f.write('in')


# initialize beacon-related stuffs

def distance(rssi):
    return sqrt(pow(10, (TXPOWER - rssi) / 10))

def scan_beacon(q, l):
    scan = sp.Popen(('node', 'location.js'), stdout=sp.PIPE)
    while True:
        addr, rssi = scan.stdout.readline().split()
        addr = addr.decode()
        if addr in distances.keys():
            rssi = int(rssi)
            with l:
                q.put((addr, rssi))

rssi = mp.Queue()
rssi_lock = mp.Lock()
BLE = mp.Process(target=scan_beacon, args=(rssi, rssi_lock))


# initialize socket; connect to data storage server

host, port = os.environ['SERVER'].split(':')
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((host, int(port)))
print('Connected to the server')

def close_socket(signal=None, frame=None):
    print('GOOD BYE!')
    server.close()
    sys.exit(0)


# main loop

(x, y, w_prev, theta_prev, theta_curr) = (0, 150, 0, 0, 0)
s_prev = False
dt = 0.01
tstart = time.perf_counter()
BLE.start()
signal.signal(signal.SIGTERM, close_socket)
signal.signal(signal.SIGINT, close_socket)
while True:
    time.sleep(t_interval)
    while imu.IMURead():
        data = imu.getIMUData()
        w_curr = data['gyro'][2]
        theta_curr += 0.5*dt*(w_prev + w_curr)
        w_prev = w_curr
    with open('/sys/class/gpio/gpio%d/value' % pin, 'rb', 0) as f:
        s_curr = f.read() == b'0\n'
    if s_prev is not s_curr:
        s_prev = s_curr
        if not s_prev:
            ts = time.perf_counter() - tstart
            tstart += ts
            theta = 0.5*(theta_prev + theta_curr)
            x += pi*diameter*cos(theta)
            y += pi*diameter*sin(theta)
            theta_prev = theta_curr
            values = []
            with rssi_lock:
                while not rssi.empty():
                    values.append(rssi.get())
            server.send(pickle.dumps((x, y, ts)))
