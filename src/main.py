'''
Created on 25 02 2013

@author: nein

requirements:
    - PyGame http://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame
    - NumPy  http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy
'''
import pygame
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
    columns=[]
        
    def __init__(self, imageRect, fractalRect, compute):
        self.ir = imageRect
        self.fr = fractalRect
        self.cp = compute
    
    def __call__(self):
        self.columns = []
        xStep = self.fr.w / self.ir.w
        yStep = self.fr.h / self.ir.h

        for x in xrange(self.ir.w):
            column = [self.cp(self.fr.l + x*xStep, self.fr.t + y*yStep) for y in xrange(self.ir.h)]
            self.columns.append(column)
        
#    mandelbrot computer
def mandelbrotCompute(x, y, maxDepth):
    z = complex(x, y)
    c = z
    for i in range(maxDepth):
        z = z*z + c
        if abs(z) > 2:
            return i*1000
    return 0
   
        

#
#    actual script
#

width = 555
height = 555
fractalRects = []
imageRects = []

#    task 1
fractalRects.append(Rect(-1.5, 0.5, -1.0, 0.0))
imageRects.append(Rect(0, width, 0, height/2))
#    task 2
fractalRects.append(Rect(-0.5, 0.5, 0.0, 1.0))
imageRects.append(Rect(width/2, width, height/2, height))
#    task 3
fractalRects.append(Rect(-1.5, -0.5, 0.0, 1.0))
imageRects.append(Rect(0, width/2, height/2, height))

compute = partial(mandelbrotCompute, maxDepth=100)

tasks = [Task(ir, fr, compute) for (ir, fr) in zip(imageRects, fractalRects)]

threadPool = ThreadPool(2)
map(threadPool.add_task, tasks)
    
pygame.init() 
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True

pixels = pygame.surfarray.pixels2d(screen)
while running:
    
    
    for task in tasks:
        if(len(task.columns)):
            pixels[task.ir.l:task.ir.l+len(task.columns), task.ir.t:task.ir.b] = task.columns

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(5)
    print pygame.time.get_ticks()



