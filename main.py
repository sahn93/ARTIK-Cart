from config import LOCATIONS, TXPOWER
from math import sqrt, pow
from subprocess import Popen, PIPE


def distance(rssi):
    return sqrt(pow(10, (TXPOWER - rssi) / 10))

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
