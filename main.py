import sys
import time
import RTIMU
from config import CALIB_FILE, LOCATIONS, TXPOWER
from math import sqrt, pow, degrees
from subprocess import Popen, PIPE


def distance(rssi):
    return sqrt(pow(10, (TXPOWER - rssi) / 10))

s = RTIMU.Settings(CALIB_FILE)
imu = RTIMU.RTIMU(s)

if (not imu.IMUInit()):
    print("IMU Init Failed")
    sys.exit(1)
else:
    print("IMU Init Succeeded: " + imu.IMUName())

imu.setSlerpPower(0.02)
imu.setGyroEnable(True)
imu.setAccelEnable(True)
imu.setCompassEnable(True)

poll_interval = imu.IMUGetPollInterval()

while True:
    if imu.IMURead():
        data = imu.getIMUData()
        accel = data["accel"]
        print("x: %f y: %f z: %f" % (accel[0],
                                     accel[1],
                                     accel[2]))
        time.sleep(poll_interval*1.0/1000.0)

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
