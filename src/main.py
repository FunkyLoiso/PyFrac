'''
Created on 25 02 2013

@author: nein
'''
import threading
import pygame
from collections import deque
from time import time, sleep

#    rectangle in fractal space
class FractalRect:
    def __init__(self, left, right, top, bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        
    def width(self):
        return abs(self.right - self.left)
    def height(self):
        return abs(self.bottom - self.top)
        
#    fractal generator (this is so elegant)
def fractalImage(width, height, fractalRect, compute):
    xStep = fractalRect.width() / width
    yStep = fractalRect.height() / height
    
    for y in range(0, height):
        line = [compute(fractalRect.left + x*xStep, fractalRect.top + y*yStep) for x in range(0, width)]
        yield line
        
#    fractal generator as functional object (this is ugly as hell)
class fractalImage2:
    def __init__(self, width, height, rect, compute):
        self.w = width
        self.h = height
        self.rect = rect
        self.xStep = rect.width() / width
        self.yStep = rect.height() / height
        self.comp = compute
        self.curLine = 0

    def __iter__(self):
        return self

    def next(self):
        if self.curLine < self.h:
            line = [self.comp(self.rect.left + x*self.xStep, self.rect.top + (self.curLine)*self.yStep) for x in range(0, self.w)]
            self.curLine = self.curLine + 1
            return line
        else:
            raise StopIteration()

#    mandelbrot computer
class mandelbrotCompute:
    def __init__(self, maxDepth):
        self.maxDepth = maxDepth
        
    def __call__(self, x0, y0):
        x = y = 0
        iteration = 0
        
        while x*x + y*y < 2*2  and  iteration < self.maxDepth:
            xtemp = x*x - y*y + x0
            y = 2*x*y + y0
            x = xtemp
            iteration = iteration + 1
        return iteration
    
#    where and how to render
class RenderTask:
    def __init__(self, image, generator):
        self.image = image
        self.generator = generator
    
    
#    thread that supports RenderTasks and stopping
class FractalThread(threading.Thread):
    _taskQueue = deque()
    _stopFlag = False
    
    def __init__(self):
        threading.Thread.__init__(self)
        
    def enqueue(self, task):
        self._taskQueue.appendleft(task)

    def run(self):
        while not self._stopFlag:
            while len(self._taskQueue) > 0:
                task = self._taskQueue.pop()
                for line in task.generator:
                    if self._stopFlag: return
                    task.image.append(line)
            sleep(0.1)
                    
    def stop(self):
        self._stopFlag = True;
            

#
#    actual script
#

image = []
width = 640
height = 400
fractalRect = FractalRect(-1.5, 0.5, -1.0, 1.0)
compute = mandelbrotCompute(100)
generator = fractalImage2(width, height, fractalRect, compute)
task = RenderTask(image, generator)
thread = FractalThread()
thread.start()
thread.enqueue(task)

pygame.init() 
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
            thread.stop()
            thread.join()

    pygame.display.flip()
    clock.tick(2)



