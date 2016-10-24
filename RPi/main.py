#!/usr/bin/python3
import os
import sys
import time
import struct
import RTIMU
import serial

# check admin rights

if os.getuid() != 0:
    print('You are not root :(')
    sys.exit(1)


# initialize serial port

tty = serial.Serial('/dev/ttyAMA0', timeout=0.1)

def close_serial(signal=None, frame=None):
    print('GOOD BYE!')
    tty.close()
    sys.exit(0)


# serial port handshaking

def handshaking(tty):
    while tty.in_waiting == 0:
        pass
    tty.write(b'A')
    tty.reset_input_buffer()

print('Waiting ARTIK...')
handshaking(tty)


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


# main loop: read sensor and send through uart

signal.signal(signal.SIGTERM, close_serial)
signal.signal(signal.SIGINT, close_serial)
handshaking(tty)
while True:
    time.sleep(t_interval)
    while imu.IMURead():
        data = imu.getIMUData()
        w_curr = data['gyro'][2]
        tty.write(struct.pack('d', w_curr))
