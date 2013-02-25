'''
Created on 25 02 2013

@author: nein
'''
#    rectangle in fractal space
class FractalRect:
    left = right = top = bottom = 0
    def __init__(self, left, right, top, bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        
    def width(self):
        return self.right - self.left
    def height(self):
        return self.bottom - self.top
        
#    fractal generator
def fractalImage(width, height, fractalRect, compute, maxDepth):
    xStep = fractalRect.width() / width
    yStep = fractalRect.height() / height
    
    for y in range(0, height):
        line = [compute(fractalRect.left + x*xStep, fractalRect.top + y*yStep, maxDepth) for x in range(0, width)]
        yield line

#mandelbrot computer    
def mandelbrotCompute(x0, y0, maxDepth):
    x = y = 0
    iteration = 0
    
    while x*x + y*y < 2*2  and  iteration < maxDepth:
        xtemp = x*x - y*y + x0
        y = 2*x*y + y0
        x = xtemp
        iteration = iteration + 1
    return iteration

import threading

image = []

class AsyncDraw(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        fractalRect = FractalRect(-1.5, 0.5, -1.0, 1.0)
        for line in fractalImage(640, 480, fractalRect, mandelbrotCompute, 100):
            image.append(line)


thread = AsyncDraw()
#thread.run = myRun
thread.start()
   
import sys
#import and init pygame
import pygame
pygame.init() 

width = 640
height = 400

screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True

while running:
    screen.lock() 
    y = 0
    for line in image:
        for x in range(0, width):
            screen.set_at((x, y), ( 255-(line[x]%41*5), 255-(line[x]%17*5), 255-(line[x]%34*5) ))
        y = y+1
    screen.unlock()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(240)


