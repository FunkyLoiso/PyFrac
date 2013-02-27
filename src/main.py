'''
Created on 25 02 2013

@author: nein
'''
import pygame
from itertools import product
from functools import partial
from pool import ThreadPool

class Rect:
    def __init__(self, left, right, top, bottom):
        self.l = left
        self.r = right
        self.t = top
        self.b = bottom
        self.w = abs(self.r - self.l)
        self.h = abs(self.b - self.t)

class Task:
    _image = []
    def __init__(self, imageRect, fractalRect, compute):
        self.ir = imageRect
        self.fr = fractalRect
        self.cp = compute
    
    def __call__(self):
        xStep = self.fr.w / self.ir.w
        yStep = self.fr.h / self.ir.h
        for (x,y) in product(xrange(self.ir.w), xrange(self.ir.h)):
            self._image.append( ((self.ir.l+x ,self.ir.t+y),                        # coordinates of pixel
                                 self.cp(self.fr.l + x*xStep, self.fr.t + y*yStep)  # value for pixel
                                ))
    
    def __iter__(self):
        return iter(self._image)
        
#    mandelbrot computer
def mandelbrotCompute(x0, y0, maxDepth):
    x = y = 0
    iteration = 0
    
    while x*x + y*y < 2*2  and  iteration < maxDepth:
        xtemp = x*x - y*y + x0
        y = 2*x*y + y0
        x = xtemp
        iteration = iteration + 1
    return iteration
   
        

#
#    actual script
#

width = 640
height = 480
fractalRect1 = Rect(-1.5, 0.5, -1.0, 0.0)
fractalRect2 = Rect(-1.5, -0.5, 0.0, 1.0)
fractalRect3 = Rect(-0.5, 0.5, 0.0, 1.0)
imageRect1 = Rect(0, width, 0, height/2)
imageRect2 = Rect(0, width/2, height/2, height)
imageRect3 = Rect(width/2, width, height/2, height)

compute = partial(mandelbrotCompute, maxDepth=100)

task1 = Task(imageRect1, fractalRect1, compute)
task2 = Task(imageRect2, fractalRect2, compute)
task3 = Task(imageRect3, fractalRect3, compute)

threadPool = ThreadPool(2)
threadPool.add_task(task1)
threadPool.add_task(task3)
threadPool.add_task(task2)
    
pygame.init() 
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True

while running:
    
    screen.lock() 
    for ((x,y), depth) in task1:
        screen.set_at((x, y), depth*1000)
    for ((x,y), depth) in task2:
        screen.set_at((x, y), depth*1000)
    for ((x,y), depth) in task3:
        screen.set_at((x, y), depth*1000)
    screen.unlock()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(30)



