from numpy import sin, cos, exp, array, pi
from scipy.integrate import solve_ivp

# PHYSICAL CONSTANTS
l = 2.0
g = 9.81
  
        
class DoublePendelumNumerics():
    '''
    Math/Numerics for Lagrangian
    L = theta_dot^2 + 1/2 phi_dot^2 + theta_dot phi_dot cos(theta - phi) + 2 g/l cos(theta) + g/l cos(phi)
    '''
    def __init__(self, theta_0=0.0, theta_dot_0=0.0, phi_0=0.0, phi_dot_0=0.0, sim_time=10.0):
        self.y0 = array([theta_0, theta_dot_0, phi_0, phi_dot_0])
        self.compute_solution(sim_time)
    
    def get_ode_rhs(self, t, y):
        # unpack
        theta, theta_dot, phi, phi_dot = y
        # auxillary variable
        R_1 = phi_dot * (theta_dot - phi_dot) * sin(theta - phi) - theta_dot * phi_dot * sin(theta - phi) - 2 * (g / l) * sin(theta)
        R_2 = theta_dot * (theta_dot - phi_dot) * sin(theta - phi) + theta_dot * phi_dot * sin(theta - phi) - (g / l) * sin(phi)
        # Euler-Lagrange equations
        theta_updated = theta_dot
        theta_dot_updated = (1 / (2 - cos(theta - phi)**2)) * (R_1 - R_2 * cos(theta - phi))
        phi_updated = phi_dot
        phi_dot_updated = (1 / (2 - cos(theta - phi)**2)) * (-R_1 * cos(theta - phi) + 2 * R_2)
        # pack
        y_updated = array([theta_updated, theta_dot_updated, phi_updated, phi_dot_updated])
        return y_updated

    def compute_solution(self, sim_time):
        solution = solve_ivp(fun=self.get_ode_rhs, t_span=(0.0, sim_time), y0=self.y0, dense_output=True)
        self.solution = solution.sol

    def get_theta_solution(self):
        def theta_function(t):
            theta, theta_dot, phi, phi_dot = self.solution(t)
            return float(theta)
        return theta_function
    
    def get_phi_solution(self):
        def phi_function(t):
            theta, theta_dot, phi, phi_dot = self.solution(t)
            return float(phi)
        return phi_function
        

