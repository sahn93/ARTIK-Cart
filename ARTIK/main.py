#!/usr/bin/python3
import os
import sys
import time
import serial
import struct
import socket
import signal
import pickle
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

pin = 12
if os.path.exists('/sys/class/gpio/gpio%d/direction' % pin):
    with open('/sys/class/gpio/unexport', 'w') as f:
        f.write(str(pin))
with open('/sys/class/gpio/export', 'w') as f:
    f.write(str(pin))
with open('/sys/class/gpio/gpio%d/direction' % pin, 'w') as f:
    f.write('in')


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
BLE.start()
signal.signal(signal.SIGTERM, close_socket)
signal.signal(signal.SIGINT, close_socket)
handshaking(tty)
while True:
    w_curr, = struct.unpack('d', tty.read(8))
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
            particles += pi*diameter*np.array([cos(theta), sin(theta)])[:, np.newaxis]
            theta_prev = theta_curr
            w = 0
            with rssi_lock:
                while not rssi_queue.empty():
                    # particle filter using t-dist
                    addr, rssi = rssi_queue.get()
                    loc = np.apply_along_axis(lambda x: pos_to_rssi(x, LOCATIONS[addr]), 0, particles)
                    w += np.log(st.t.cdf(rssi+0.5, 4, loc, 2) - st.t.cdf(rssi-0.5, 4, loc, 2))
            w = np.exp(w)
            particles = particles[:, np.random.choice(N, N, p = w/sum(w))]
            x, y = np.mean(particles, 1)
            server.send(pickle.dumps((x, y, ts)))
