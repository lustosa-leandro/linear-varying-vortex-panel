import lvvp
import numpy
import math

# reads geometry from a data file -- further work is mandatory here for generality!
# we assume here file is composed ONLY by coordinates. all extra lines need to be deleted
with open ('./airfoils/mh45.dat') as file_name:
    x, z = numpy.loadtxt(file_name, dtype=float, unpack=True)

N = 100                   # number of panels
AOA = 0.0*math.pi/180.0   # angle of attack
v_wind = 1                # wind relative speed

# discretizes of the geometry into panels
panels = lvvp.define_panels(x, z, N)

# linear varying vortex panels linear system setup
freestream = lvvp.Freestream(v_wind, AOA)
b = lvvp.rhs_setup(panels, freestream)
A = lvvp.lhs_setup(panels)
vortices = numpy.linalg.solve(A,b)

# plot results
lvvp.airfoil_flow_plot(panels, vortices, freestream)

