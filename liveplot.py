#!/usr/bin/python3

import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def animate(i):
	graph_data = open('coordinates.csv','r').read()
	lines = graph_data.split('\n')
	lines = lines[1:]
	xs = []
	ys = []
	for line in lines:
		if len(line) > 1:
			x, y, t = line.split(',')
			xs.append(x)
			ys.append(y)
	
	ax1.clear()
	ax1.plot(xs, ys)

ani = animation.FuncAnimation(fig, animate, interval = 100)
plt.show()