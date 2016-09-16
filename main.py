from config import LOCATIONS
from subprocess import Popen, PIPE


RSSI = {beacon: None for beacon in LOCATIONS}

with Popen(['node', 'location.js'], stdout=PIPE) as scan:
    while True:
        addr, rssi = scan.stdout.readline().split()
        addr = addr.decode()
        if addr in RSSI.keys():
            RSSI[addr] = int(rssi)
        if all(RSSI.values()):
            print(RSSI)  # TODO
