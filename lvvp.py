import math 
import numpy 
from matplotlib import pyplot 

# generates mesh of grid points
N = 50 
x_start, x_end = -2.0, 2.0 
y_start, y_end = -1.0, 1.0 
x = numpy.linspace(x_start, x_end, N) 
y = numpy.linspace(y_start, y_end, N)

X, Y = numpy.meshgrid(x,y)

# plot of point grid
size = 10 
pyplot.figure(figsize=(size,(y_end-y_start)/(x_end-x_start)*size)) 
pyplot.xlabel('x', fontsize=16) 
pyplot.ylabel('y', fontsize=16) 
pyplot.xlim(x_start, x_end) 
pyplot.ylim(y_start, y_end) 
pyplot.scatter(X, Y, s=10, color='#CD2305', marker='o', linewidth=1) 
pyplot.show() 

