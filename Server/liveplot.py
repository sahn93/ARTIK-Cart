#!/usr/bin/python3

import os
import sys
import json
import signal
import socket
import pygame
import queue
import threading
from pygame.locals import *

pygame.init()
FPS = 60
fpsClock = pygame.time.Clock()
width = 1366
height = 768
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
pygame.display.set_caption("FANTASTIC BABY")

q = queue.Queue()
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
BG = Color("#89CEBA")
logo = pygame.transform.scale(pygame.image.load("artik.png"), (780//2, 270//2))
x, y, theta, t = (None, None, None, None)
#x, y, theta, t = (50, 50, 0, 0)
dx, dy = (84, 84)
receive = threading.Thread(target=f, args=(q,))
receive.start()
while not done:
    for event in pygame.event.get():
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            done = True
    screen.fill(BG)
    pygame.draw.rect(screen, Color("white"), (dx, dy, 800, 600), 4)
    screen.blit(logo, (930, 300))
    col = Color("white" if frame < 30 else "red")
    if t is not None:
        pygame.draw.circle(screen, col, (int(x)+dx, int(y)+dy), 10)
    pygame.display.update()
    try:
        data = q.get_nowait()
        print(data)
        x, y, theta, t = json.loads(data.decode('utf-8'))
    except:
        pass
    frame = (frame+1)%FPS
    fpsClock.tick(FPS)

pygame.quit()
sys.exit(0)
