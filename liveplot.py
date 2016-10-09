#!/usr/bin/python3

import sys
import signal
import socket
import pickle
import matplotlib.pyplot as plt
import matplotlib.animation as animation

host, port = os.environ['SERVER'].split(':')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(True)
conn, addr = s.accept()

w = open('./data.csv', 'w')
w.write('x, y, t\n')

def safe_close(signal=None, frame=None):
    print('GOOD BYE!')
    w.close()
    sys.exit(0)
signal.signal(signal.SIGTERM, safe_close)
signal.signal(signal.SIGINT, safe_close)

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax1.set_xlim([0,300])
ax1.set_ylim([0,300])

xs = []
ys = []

def animate(i):
    data = conn.recv(4096)
    x, y, t = pickle.loads(data)
    print((x, y, t))
    w.write("%f, %f, %f\n" % (x, y, t))
    xs.append(x)
    ys.append(y)
    ax1.clear()
    ax1.set_xlim([0,300])
    ax1.set_ylim([0,300])
    ax1.plot(xs, ys)

ani = animation.FuncAnimation(fig, animate, interval = 100)
plt.show()
conn.close()
