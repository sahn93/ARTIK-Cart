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

def handshaking(tty, phase):
    while True:
        tmp = tty.read()
        if tmp == phase:
            break
        elif tmp == b'K':
            tty.close()
            sys.exit(0)
        time.sleep(0.1)
    tty.write(phase)
    tty.reset_input_buffer()
print('Waiting ARTIK...')
tty = serial.Serial('/dev/ttyAMA0', timeout=0)
handshaking(tty, b'A')


# initialize gyroscope

s = RTIMU.Settings("config")
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

handshaking(tty, b'B')
while tty.read() != b'K':
    time.sleep(t_interval)
    while imu.IMURead():
        data = imu.getIMUData()
        w_curr = data['gyro'][2]
        print(w_curr)
        tty.write(struct.pack('d', w_curr))
tty.close()
