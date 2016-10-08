#!/usr/bin/python3
import RTIMU
import signal
from config import CALIB_FILE, LOCATIONS, TXPOWER


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

if imu.IMURead():
    print("Success")
else:
    print("Fail")
