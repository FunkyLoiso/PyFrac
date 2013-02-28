'''
Created on 25 02 2013

@author: nein

requirements:
    - PyGame http://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame
    - NumPy  http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy
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
    _image=[]
        
    def __init__(self, imageRect, fractalRect, compute):
        self.ir = imageRect
        self.fr = fractalRect
        self.cp = compute
    
    def __call__(self):
        self._image = []
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

while running:
    
    for task in tasks:
        pixels = pygame.surfarray.pixels2d(screen)
        for ((x,y), depth) in task:
            pixels[x,y] = depth*1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    print clock.tick(30)



