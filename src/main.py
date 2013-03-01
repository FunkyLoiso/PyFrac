'''
Created on 25 02 2013

@author: nein

requirements:
    - PyGame http://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame
    - NumPy  http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy
'''
import pygame
from functools import partial
#from pool import ThreadPool
from multiprocessing import Pool, Manager
from Queue import Empty

class Rect:
    def __init__(self, left, right, top, bottom):
        self.l = left
        self.r = right
        self.t = top
        self.b = bottom
        self.w = abs(self.r - self.l)
        self.h = abs(self.b - self.t)

class Task:
    def __init__(self, imageRect, fractalRect, compute):
        self.ir = imageRect
        self.fr = fractalRect
        self.cp = compute
    
    def __call__(self, queue):
        xStep = self.fr.w / self.ir.w
        yStep = self.fr.h / self.ir.h

        for x in xrange(self.ir.w):
            queue.put( (x, [self.cp(self.fr.l + x*xStep, self.fr.t + y*yStep) for y in xrange(self.ir.h)]) )
        
#    mandelbrot computer
def mandelbrotCompute(x, y, maxDepth):
    z = complex(x, y)
    c = z
    for i in range(maxDepth):
        z = z*z + c
        if abs(z) > 2:
            return i * 1000
    return 0

#
def divideTask(task, parts):
    iHeight = task.ir.h / parts
    fHeight = task.fr.h / parts
    tasks = []
    
    iPartTop = task.ir.t
    fPartTop = task.fr.t
    for _ in range(parts-1):
        imageRect = Rect(task.ir.l, task.ir.r, iPartTop, iPartTop+iHeight)
        iPartTop += iHeight
        fractalRect = Rect(task.fr.l, task.fr.r, fPartTop, fPartTop+fHeight)
        fPartTop += fHeight
        tasks.append(Task(imageRect, fractalRect, task.cp))
    # last part
    imageRect = Rect(task.ir.l, task.ir.r, iPartTop, task.ir.b)
    fractalRect = Rect(task.fr.l, task.fr.r, fPartTop, task.fr.b)
    tasks.append(Task(imageRect, fractalRect, task.cp))
    
    return tasks   

#
#    actual script
#
width = 555
height = 555
imageRect = Rect(0, width, 0, height)
fractalRect = Rect(-1.5, 0.5, -1.0, 1.0)
compute = partial(mandelbrotCompute, maxDepth=100)

task = Task(imageRect, fractalRect, compute)
tasks = divideTask(task, 10)
  
if __name__ == "__main__":
    pygame.init() 
    screen = pygame.display.set_mode((width, height))
    screen.fill((150, 150, 150))
    clock = pygame.time.Clock()
    pixels = pygame.surfarray.pixels2d(screen)
    
    manager = Manager()
    pool = Pool()
    for i in range(len(tasks)):
        task = tasks[i]
        task.queue = manager.Queue()
        pool.apply_async(task, (task.queue, ))
        
    running = True
    while running:
        for task in tasks:
            while True:
                try:
                    (x, column) = task.queue.get_nowait()
                except Empty:
                    break 
                pixels[x, task.ir.t:task.ir.b] = column
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
        pygame.display.flip()
        clock.tick(5)
        pygame.display.set_caption(str(pygame.time.get_ticks()))
    


