from subprocess import Popen, PIPE


LOCATIONS = {'88:c2:55:10:f7:38': None,
             '88:c2:55:10:31:17': None,
             '88:c2:55:11:10:1b': None}


RSSI = {beacon: None for beacon in LOCATIONS}

with Popen(['node', 'location.js'], stdout=PIPE) as scan:
    while True:
        addr, rssi = scan.stdout.readline().split()
        addr = addr.decode()
        if addr in RSSI.keys():
            RSSI[addr] = int(rssi)
        if all(RSSI.values()):
            print(RSSI)  # TODO
