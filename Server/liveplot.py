#!/usr/bin/python3

import os
import sys
import json
import signal
import socket
import pygame
import multiprocessing as mp
from pygame.locals import *

pygame.init()
FPS = 60
fpsClock = pygame.time.Clock()
#width = 1366
#height = 768
width = 800
height = 600
screen = pygame.display.set_mode((width, height))
#pygame.display.toggle_fullscreen()

q = mp.Queue()
def f(q):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 54321))
    s.listen(True)
    conn, addr = s.accept()
    while True:
        q.put(conn.recv(1024))

frame = 0
done = False
x, y, theta, t = (None, None, None, None)
receive = mp.Process(target=f, args=(q,))
receive.start()
while not done:
    for event in pygame.event.get():
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            done = True
    screen.fill(Color("#89CEBA"))
    if t is not None:
        pygame.draw.circle(screen, Color("white"), (x, y), 10)
    pygame.display.update()
    try:
        data = q.get_nowait()
        print(data)
        x, y, theta, t = json.loads(data.decode('utf-8'))
    except:
        pass
    frame += 1
    fpsClock.tick(FPS)

receive.terminate()
pygame.quit()
