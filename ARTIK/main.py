#!/usr/bin/python3
import os
import sys
import time
import serial
import struct
import socket
import signal
import json
import numpy as np
import scipy.stats as st
import subprocess as sp
import multiprocessing as mp
from math import pi, sqrt, pow, degrees, cos, sin
from config import LOCATIONS, TXPOWER


# check admin rights

if os.getuid() != 0:
    print('You are not root :(')
    sys.exit(1)


# initialize light sensor

ANALOG_BASE = '/sys/devices/12d10000.adc/iio:device0/in_voltage%d_raw'
PIN_WHEEL_REV = 0
PIN_WHEEL_ANGLE = 1


# initialize beacon-related stuffs

n = 2
h = 200
def pos_to_rssi(mypos, beaconpos):
    diff = mypos - beaconpos
    distance = sqrt(h**2+diff[0]**2+diff[1]**2)
    return TXPOWER-10*n*np.log10(distance)

def scan_beacon(q, l):
    scan = sp.Popen(('node', 'location.js'), stdout=sp.PIPE)
    scan.stdout.readline()
    while True:
        addr, rssi = scan.stdout.readline().decode().split(',')
        if addr in distances.keys():
            rssi = int(rssi)
            with l:
                q.put((addr, rssi))

rssi_queue = mp.Queue()
rssi_lock = mp.Lock()
BLE = mp.Process(target=scan_beacon, args=(rssi_queue, rssi_lock))


# initialize socket; connect to data storage server

host, port = os.environ['SERVER'].split(':')
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((host, int(port)))
print('Connected to the server')


# initialize serial port

tty = serial.Serial('/dev/ttySAC1', timeout=0.1)

def close_socket(signal=None, frame=None):
    print('GOOD BYE!')
    server.close()
    tty.close()
    sys.exit(0)


# serial port handshaking

def handshaking(tty):
    while tty.in_waiting == 0:
        tty.write(b'A')
        time.sleep(0.1)
    tty.reset_input_buffer()

print('Waiting RPi...')
handshaking(tty)


# main loop

diameter = 3.4
s_prev = False
dt = 0.01
tstart = time.perf_counter()
(w_prev, theta_prev, theta_curr) = (0, 0, 0)
mu = np.array([0, 150])
Sigma = np.diag([5, 5])
N = 1000
particles = np.random.multivariate_normal(mu, Sigma, N).T
x, y = np.mean(particles, 1)
signal.signal(signal.SIGTERM, close_socket)
signal.signal(signal.SIGINT, close_socket)
handshaking(tty)
while True:
    w_curr, = struct.unpack('d', tty.read(8))
    theta_curr += 0.5*dt*(w_prev + w_curr)
    w_prev = w_curr
    with open(ANALOG_BASE % PIN_WHEEL_ANGLE, 'rb', 0) as f:
        tmp = int(f.read())
        if tmp < 200:
            theta_diff = 0
        elif tmp < 400:
            theta_diff = pi*0.5
        elif tmp < 535:
            theta_diff = pi*1.5
        else:
            theta_diff = pi
    with open(ANALOG_BASE % PIN_WHEEL_REV, 'rb', 0) as f:
        s_curr = int(f.read()) < 300
    if s_prev is not s_curr:
        s_prev = s_curr
        if not s_prev:
            ts = time.perf_counter() - tstart
            tstart += ts
            theta = 0.5*(theta_prev + theta_curr)
            particles += pi*diameter*np.array([cos(theta+theta_diff), sin(theta+theta_diff)])[:, np.newaxis]
            theta_prev = theta_curr
            x, y = np.mean(particles, 1)
            server.send(json.dumps((x, y, ts)).encode('utf-8'))
