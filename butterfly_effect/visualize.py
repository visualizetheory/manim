from config import *
from numerics import *


# CUSTOM MOBJECTS

class DoublePendelum(VGroup):
    def __init__(self, theta, phi, color=WHITE):
        start_point = ax.c2p(0, 0)
        middle_point = ax.c2p(l * sin(theta), - l * cos(theta))
        end_point = ax.c2p(l * sin(theta) + l * sin(phi), - l * cos(theta) - l * cos(phi))

        first_line = Line(start_point, middle_point)
        second_line = Line(middle_point, end_point)

        first_dot = Dot(middle_point)
        second_dot = Dot(end_point)

        super().__init__(first_line, first_dot, second_line, second_dot)
        self.set_color(color)

class MotionTracker(ParametricFunction):
    def __init__(self, theta, phi, t_end, **kwargs):
        delta_t = 1.5
        t_start = t_end - delta_t if t_end > delta_t else 0.0
        super().__init__(
            lambda t: ax.c2p(l * sin(theta(t)) + l * sin(phi(t)), - l * cos(theta(t)) - l * cos(phi(t))),
            t_range=(t_start, t_end),
            **kwargs
        )

class DynamicDoublePendelum(VGroup):
    def __init__(self, t, theta_0, phi_0, sim_time, color):
        super().__init__()
        self.compute_solution(theta_0, phi_0, sim_time)
        self.add_pendelum(t, color)
        self.add_tracker(t, color)
    
    def compute_solution(self, theta_0, phi_0, sim_time):
        self.numerics = DoublePendelumNumerics(theta_0=theta_0, phi_0=phi_0, sim_time=sim_time)
        self.theta = self.numerics.get_theta_solution()
        self.phi = self.numerics.get_phi_solution()

    def add_pendelum(self, t, color):
        self.pendelum = DoublePendelum(self.theta(t.get_value()), self.phi(t.get_value()), color=color)
        self.pendelum.add_updater(lambda mob: mob.become(
            DoublePendelum(self.theta(t.get_value()), self.phi(t.get_value()), color=color)  
        ))
        self += self.pendelum

    def add_tracker(self, t, color):
        self.tracker = MotionTracker(self.theta, self.phi, t.get_value(), color=color)
        self.tracker.add_updater(lambda mob: mob.become(
            MotionTracker(self.theta, self.phi, t.get_value(), color=color)
        ))
        self += self.tracker

# parameters
sim_time = 32.0
epsilon = 0.05

first_theta_0 = 120*DEGREES
first_phi_0 = -90*DEGREES
first_color = "#FA0202"

second_theta_0 = first_theta_0
second_phi_0 = first_phi_0 + epsilon
second_color = "#2CFA02"

title_color = "#1bd7ea"

# axes
ax = Axes(x_range=(-2.0, 2.0), x_length=1.3*4.0, y_range=(-4.0, 1.0), y_length=1.3*5.0).shift(0.5*DOWN).set_opacity(0.3)

# updater for pendelums
t = ValueTracker(0.0)

# pendelums
first_dynamic_pendelum = DynamicDoublePendelum(t, first_theta_0, first_phi_0, sim_time, first_color)
second_dynamic_pendelum = DynamicDoublePendelum(t, second_theta_0, second_phi_0, sim_time, second_color)

first_dynamic_pendelum_copy = first_dynamic_pendelum.copy()

# title
title = Tex(r"\textbf{$\mathbb{B}$", r"utterfly effect.}", height=0.7).move_to(5*UP)
title[0].set_color(title_color)

# SCENE
class ButterflyEffectScene(Scene):
    def construct(self):
        self.add(ax, first_dynamic_pendelum, first_dynamic_pendelum_copy, title)
        self.play(ReplacementTransform(first_dynamic_pendelum_copy, second_dynamic_pendelum))
        self.play(t.animate.set_value(sim_time), run_time=sim_time, rate_func=linear)
        self.wait()        
