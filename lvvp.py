import math 
import numpy 
from matplotlib import pyplot 

class Freestream:
    """Contains information related to a freestream.
    """
    def __init__(self, v_inf, alpha):
        self.v_inf = v_inf
        self.alpha = alpha

    def velocity(self, X, Z):
        self.u = self.v_inf*math.cos(self.alpha)+X*0.0
        self.w = self.v_inf*math.sin(self.alpha)+X*0.0

class Source:
    """Contains information related to a source (or a sink).
    """
    def __init__(self, strength, x, y):
        """Initializes the singularity.

        Arguments
        ------------
        strength -- strength of the singularity.
        x, y -- coordinates of the singularity.
        """
        self.strength = strength
        self.x, self.y = x, y

    def velocity(self, X, Y):
        """Computes the velocity field generated by the singularity.

        Arguments
        -----------
        X, Y -- mesh grid.
        """
        self.u = self.strength/(2*math.pi)*(X-self.x)/((X-self.x)**2+(Y-self.y)**2)
        self.v = self.strength/(2*math.pi)*(Y-self.y)/((X-self.x)**2+(Y-self.y)**2)

    def stream_function(self, X, Y):
        """Computes the stream-function generated by the singularity.
    
        Arguments
        ------------
        X, Y -- mesh grid.
        """
        self.psi = self.strength/(2*math.pi)*numpy.arctan2((Y-self.y), (X-self.x))

class Vortex:
    """Contains information related to a vortex.
    """
    def __init__(self, strength, x, y):
        """Initializes the vortex.

        Arguments
        ------------
        strength -- strength of the vortex.
        x, y -- coordinates of the vortex.
        """
        self.strength = strength
        self.x, self.y = x, y

    def velocity(self, X, Y):
        """Computes the velocity field generated by a vortex.

        Arguments
        ------------
        X, Y -- mesh grid.
        """
        self.u = +self.strength/(2*math.pi)*(Y-self.y)/((X-self.x)**2+(Y-self.y)**2)
        self.v = -self.strength/(2*math.pi)*(X-self.x)/((X-self.x)**2+(Y-self.y)**2)

    def stream_function(self, X, Y):
        """Computes the stream-function generated by a vortex.

        Arguments
        -----------
        X, Y -- mesh grid.
        """
        self.psi = -self.strength/(4*math.pi)*numpy.log((X-self.x)**2+(Y-self.y)**2)

class Doublet:
    """Contains information related to a doublet.
    """
    def __init__(self, strength, x, y):
        """Initializes the doublet.

        Arguments
        -----------
        strength -- strength of the doublet.
        x, y -- coordinates of the doublet.
        """
        self.strength = strength
        self.x, self.y = x, y

    def velocity(self, X, Y):
        """Computes the velocity field generated by a doublet.

        Arguments
        -----------
        X, Y -- mesh grid.
        """
        self.u = -self.strength/(2*math.pi)*\
            ((X-self.x)**2-(Y-self.y)**2)/((X-self.x)**2+(Y-self.y)**2)**2
        self.v = -self.strength/(2*math.pi)*\
            2*(X-self.x)*(Y-self.y)/((X-self.x)**2+(Y-self.y)**2)**2

    def stream_function(self, X, Y):
        """Computes the stream-function generated by a doublet.

        Arguments
        -----------
        X, Y -- mesh grid.
        """
        self.psi = -self.strength/(2*math.pi)*(Y-self.y)/((X-self.x)**2+(Y-self.y)**2)

class Panel:
    """Contains information related to a panel.
    """
    def __init__(self, xa, za, xb, zb):
        """Creates a panel.

        Arguments
        -----------
        xa, za -- Cartesian coordinates of the first end-point.
        xb, zb -- Cartesian coordinates of the second end-point.
        """
        self.xa, self.za = xa, za
        self.xb, self.zb = xb, zb
        # control-point (center-point)
        self.xc, self.zc = (xa+xb)/2.0, (za+zb)/2.0
        # length of the panel
        self.length = math.sqrt( (xb-xa)**2+(zb-za)**2 )

        # orientation of the panel (angle between x-axis and panel's normal)
        if xb-xa <= 0.:
            self.beta = math.acos( (zb-za)/self.length )
        elif xb-xa > 0.:
            self.beta = math.pi + math.acos(-(zb-za)/self.length)
        # normal unit vector
        self.nx, self.nz = math.cos(self.beta), math.sin(self.beta) 

        # location of the panel
        if self.beta <= math.pi:
            self.loc = 'upper'
        else:
            self.loc = 'lower'


def define_panels(x, z, N=40):
    """Discretizes airfoil geometry into panels using the 'cosine' method.

    Arguments
    ------------
    x, z -- Cartesian coordinates of the geometry (1D arrays).
    N -- number of panels (default 40).

    Returns
    -----------
    panels -- Numpy array of panels.
    """

    # protects against odd number of panels (which bugs the code)
    if N%2 == 1:
        N = N-1

    R = (x.max()-x.min())/2.                # radius of the ci
    R -= 1.0/10000.0*R                      # radius correction for float precision correction
    x_center = (x.max()+x.min())/2.         # x-coord of the center
    # x-coord of the circle points
    x_circle = x_center + R*numpy.cos(numpy.linspace(0,2*math.pi,N+1)) 

    x_ends = numpy.copy(x_circle)     # projection of the x-coord on the surface
    z_ends = numpy.empty_like(x_ends) # initialization of the z-coord Numpy array 

    # extend geometry array to end and begin with same x-coord (largest one)
    if x[0] < x[-1]:
        x, z = numpy.append(x[-1], x), numpy.append(z[-1], z) 
    elif x[0] > x[-1]:
        x, z = numpy.append(x, x[0]), numpy.append(z, z[0])
    else:
        pass # if both ends are equal, we do not need to close the contour

    # computes the z-coordinate of end-points
    I = 0
    for i in range(N):
        while I < len(x)-1:
            if (x[I] <= x_ends[i] <= x[I+1]) or (x[I+1] <= x_ends[i] <= x[I]):
                break
            else:
                I += 1
        a = (z[I+1]-z[I])/(x[I+1]-x[I])
        b = z[I+1] - a*x[I+1]
        z_ends[i] = a*x_ends[i] + b
    z_ends[N] = z_ends[0]

    panels = numpy.empty(N, dtype=object)
    for i in range(N):
        panels[i] = Panel(x_ends[i], z_ends[i], x_ends[i+1], z_ends[i+1])

    return panels


def lhs_setup(panels):
    """Left-hand side set-up of the linear system of equations.
    """
    # number of panels
    nPanels = len(panels)
    # left-hand size memory allocation
    LHS = numpy.zeros((nPanels+1,nPanels+1), dtype=float) 

    # loops through all panels mid-points to secure flow tangency condition
    for i in range(nPanels):
        # loops through all panel end-points 
        ni = numpy.array([panels[i].nx, panels[i].nz])
        ri = numpy.array([panels[i].xc, panels[i].zc])
        for j in range(nPanels):
            vel = panel_contribution(panels[j], ri, 1.0, 0.0, DELTA_THRSH=0.0)
            LHS[i,j  ] += numpy.dot(ni,vel)
            vel = panel_contribution(panels[j], ri, 0.0, 1.0, DELTA_THRSH=0.0)
            LHS[i,j+1] += numpy.dot(ni,vel)
    # kutta condition (net vortex density equal to zero at both end-points in trailing edge)
    LHS[nPanels,0], LHS[nPanels,nPanels] = 1, 1

    return LHS


def rhs_setup(panels, freestream):
    """Left-hand side set-up of the linear system of equations.
    """
    # number of panels
    nPanels = len(panels)
    # right-hand size memory allocation
    RHS = numpy.zeros(nPanels+1, dtype=float)

    u = freestream.v_inf*math.cos(freestream.alpha)
    w = freestream.v_inf*math.sin(freestream.alpha)

    for i in range(nPanels):
        RHS[i] = -u*panels[i].nx-w*panels[i].nz

    return RHS

def panel_contribution(panel, ri, gj, gj1, DELTA_THRSH=0.0):

    # allocate memory for velocity computation
    vel = numpy.zeros((2,1))

    # one-time operations common for all terms of the total integral
    Lj = panel.length
    rj = numpy.array([panel.xa, panel.za])
    rj1 = numpy.array([panel.xb, panel.zb])
    Aji = ri - rj
    Bj = rj - rj1
    P = 2*numpy.dot(Aji, Bj)
    A = numpy.dot(Aji, Aji)
    B = numpy.dot(Bj, Bj)
    delta = 4*A*B - P**2
    delta_convergence = True
    if delta <= DELTA_THRSH:
        delta_convergence = False 

    # Fji integral term for positive delta
    def Fji(A, B, P, x):
        I = 0.0
        I += P*math.atan((2*B*x+P)/math.sqrt(delta))/(B*math.sqrt(delta))
        I += 2*math.atan((2*B*x+P)/math.sqrt(delta))/math.sqrt(delta)
        I += -math.log(A+x*(B*x+P))/(2*B)
        return I

    def Fjj(A, B, P, x):
        I = 0.0
        I += P**2*math.atan((2*B*x+P)/math.sqrt(delta))/(B**2*math.sqrt(delta))
        I += -P*math.log(A+x*(B*x+P))/(2*B**2)
        I += 2*P*math.atan((2*B*x+P)/math.sqrt(delta))/(B*math.sqrt(delta))
        I += -2*A*math.atan((2*B*x+P)/math.sqrt(delta))/(B*math.sqrt(delta))
        I += 2*math.atan((2*B*x+P)/math.sqrt(delta))/math.sqrt(delta)
        I += -math.log(A+x*(B*x+P))/B
        I += x/B
        I += -1.0/B
        return I

    def Fjj1(A, B, P, x):
        I = 0.0
        I += -P**2*math.atan((2*B*x+P)/math.sqrt(delta))/(B**2*math.sqrt(delta))
        I += P*math.log(A+x*(B*x+P))/(2*B**2)
        I += -P*math.atan((2*B*x+P)/math.sqrt(delta))/(B*math.sqrt(delta))
        I += 2*A*math.atan((2*B*x+P)/math.sqrt(delta))/(B*math.sqrt(delta))
        I += math.log(A+x*(B*x+P))/(2*B)
        I += -x/B
        return I

    def Fj1i(A, B, P, x):
        I = 0.0
        I += math.log(A+B*x**2+P*x)/(2*B)
        I += -P*math.atan((2*B*x+P)/math.sqrt(delta))/(B*math.sqrt(delta))
        return I

    def Fj1j(A, B, P, x):
        I = 0.0
        I += Fjj1(A, B, P, x)
        return I

    def Fj1j1(A, B, P, x):
        I = 0.0
        I += -(2*A*B-P**2)*math.atan((2*B*x+P)/math.sqrt(delta))/(B**2*math.sqrt(delta)) 
        I += -P*math.log(A+B*x**2+P*x)/(2*B**2)
        I += x/B
        return I

    # Integral terms for ill delta == 0
    def Fji0(A, B, P, x):
        I = 0.0
        I += -P/(B*(2*B*x+P))
        I += -2.0/(2*B*x+P)
        I += -P*math.log(math.fabs(2*B*x+P))/(B*(2*B*x+P))
        I += -2*x*math.log(math.fabs(2*B*x+P))/(2*B*x+P)
        return I

    def Fjj0(A, B, P, x):
        I = 0.0
        I += -P**2/(2*B**2*(2*B*x+P))
        I += -P**2*math.log(math.fabs(2*B*x+P))/(B**2*(2*B*x+P))
        I += 2*x**2/(2*B*x+P)
        I += P*x/(B*(2*B*x+P))
        I += -3*P/(B*(2*B*x+P))
        I += -2*x/(2*B*x+P)
        I += -2.0/(2*B*x+P)
        I += -2*P*x*math.log(math.fabs(2*B*x+P))/(B*(2*B*x+P))
        I += -2*P*math.log(math.fabs(2*B*x+P))/(B*(2*B*x+P))
        I += -4*x*math.log(math.fabs(2*B*x+P))/(2*B*x+P)
        return I

    def Fjj10(A, B, P, x):
        I = 0.0
        I += B*(-2*B*x**2-2*P*x+P)/(B**2*(2*B*x+P))
        I += (B+P)*(2*B*x+P)*math.log(math.fabs(2*B*x+P))/(B**2*(2*B*x+P))
        return I

    def Fj1i0(A, B, P, x):
        I = 0.0
        I += ((2*B*x+P)*math.log(math.fabs(2*B*x+P))+P)/(B*(2*B*x+P))
        return I

    def Fj1j0(A, B, P, x):
        I = 0.0
        I += Fjj10(A, B, P, x)
        return I

    def Fj1j10(A, B, P, x):
        I = 0.0
        I += -P**2/(2*B**2*(2*B*x+P))
        I += -P*math.log(math.fabs(2*B*x+P))/B**2
        I += x/B
        return I

    # notice that all target velocities at ri are well defined except for the panels end-poits!!!
    if delta_convergence:
        # in case of a target point not aligned with the panel
        vc = ri
        vel += 1.0/(2*math.pi)*gj *numpy.array([[vc[1]],[-vc[0]]])*Lj*(Fji(A,B,P,1)-Fji(A,B,P,0))
        vc = rj
        vel -= 1.0/(2*math.pi)*gj *numpy.array([[vc[1]],[-vc[0]]])*Lj*(Fjj(A,B,P,1)-Fjj(A,B,P,0))
        vc = rj1
        vel -= 1.0/(2*math.pi)*gj *numpy.array([[vc[1]],[-vc[0]]])*Lj*(Fjj1(A,B,P,1)-Fjj1(A,B,P,0))
        vc = ri
        vel += 1.0/(2*math.pi)*gj1*numpy.array([[vc[1]],[-vc[0]]])*Lj*(Fj1i(A,B,P,1)-Fj1i(A,B,P,0))
        vc = rj
        vel -= 1.0/(2*math.pi)*gj1*numpy.array([[vc[1]],[-vc[0]]])*Lj*(Fj1j(A,B,P,1)-Fj1j(A,B,P,0))
        vc = rj1
        vel -= 1.0/(2*math.pi)*gj1*numpy.array([[vc[1]],[-vc[0]]])*Lj*(Fj1j1(A,B,P,1)-Fj1j1(A,B,P,0))
    else:
        # in the ill defined case of a target aligned with the panel
        vc = ri
        vel += 1.0/(2*math.pi)*gj *numpy.array([[vc[1]],[-vc[0]]])*Lj*(Fji0(A,B,P,1)-Fji0(A,B,P,0))
        vc = rj
        vel -= 1.0/(2*math.pi)*gj *numpy.array([[vc[1]],[-vc[0]]])*Lj*(Fjj0(A,B,P,1)-Fjj0(A,B,P,0))
        vc = rj1
        vel -= 1.0/(2*math.pi)*gj *numpy.array([[vc[1]],[-vc[0]]])*Lj*(Fjj10(A,B,P,1)-Fjj10(A,B,P,0))
        vc = ri
        vel += 1.0/(2*math.pi)*gj1*numpy.array([[vc[1]],[-vc[0]]])*Lj*(Fj1i0(A,B,P,1)-Fj1i0(A,B,P,0))
        vc = rj
        vel -= 1.0/(2*math.pi)*gj1*numpy.array([[vc[1]],[-vc[0]]])*Lj*(Fj1j0(A,B,P,1)-Fj1j0(A,B,P,0))
        vc = rj1
        vel -= 1.0/(2*math.pi)*gj1*numpy.array([[vc[1]],[-vc[0]]])*Lj*(Fj1j10(A,B,P,1)-Fj1j10(A,B,P,0))

    return vel    


def panels_contribution(panels, vortices, X, Y):
    """Evaluates the contribution of all panels at mesh grid.
    """

    # number of panels
    nPanels = len(panels)

    i_max = X.shape[0]
    j_max = X.shape[1]

    u_flow = numpy.zeros(X.shape,dtype=float)
    w_flow = numpy.zeros(X.shape,dtype=float)

    # loops through grid
    for i in range(i_max):
        for j in range(j_max):
            # loops through all panel end-points 
            ri = numpy.array([X[i,j], Y[i,j]])
            vel = numpy.zeros((2,1), dtype=float)
            for k in range(nPanels):
                vel += panel_contribution(panels[k], ri, vortices[k], vortices[k+1], DELTA_THRSH=0.0)  
            u_flow[i,j] = vel[0]
            w_flow[i,j] = vel[1]

    return [u_flow,w_flow]

def airfoil_flow_plot(panels, vortices, freestream, val_x=1, val_z=2, size=10):

    # sets up framing parameters for plotting 
    val_x, val_z = 1, 2
    x_min, x_max = min(panel.xa for panel in panels), max(panel.xa for panel in panels)
    z_min, z_max = min(panel.za for panel in panels), max(panel.za for panel in panels)
    x_start, x_end = x_min-val_x*(x_max-x_min), x_max+val_x*(x_max-x_min)
    z_start, z_end = z_min-val_z*(z_max-z_min), z_max+val_z*(z_max-z_min)

    # plots the geometry and the panels
    size = 10
    pyplot.figure(figsize=(size, (z_end-z_start)/(x_end-x_start)*size))
    pyplot.grid(True)
    pyplot.xlabel('x', fontsize=16)
    pyplot.ylabel('z', fontsize=16)
    pyplot.xlim(x_start, x_end)
    pyplot.ylim(z_start, z_end)
    pyplot.plot(numpy.append([panel.xa for panel in panels], panels[0].xa),
         numpy.append([panel.za for panel in panels], panels[0].za),
         linestyle='-', linewidth=1, marker='o', markersize=6, color='#CD2305');

    x = numpy.linspace(x_start, x_end, 15)
    y = numpy.linspace(z_start, z_end, 15)
    X, Y = numpy.meshgrid(x, y)
    [u_flow, w_flow] = panels_contribution(panels, vortices, X, Y)
    freestream.velocity(X,Y)
    u_flow = u_flow.copy() + freestream.u.copy()
    w_flow = w_flow.copy() + freestream.w.copy()

    # fill airfoil plot (cosmetics)
    pyplot.fill([panel.xc for panel in panels],
        [panel.zc for panel in panels],
        color='k', linestyle='solid', linewidth=2, zorder=2)

    # plot flow streamlines
    pyplot.streamplot(X, Y, u_flow, w_flow, density=2, linewidth=1, arrowsize=1, arrowstyle='->')

    # show figures
    pyplot.show()


