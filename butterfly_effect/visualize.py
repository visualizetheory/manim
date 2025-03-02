from config import *
from numerics import *


ax = Axes(x_range=(-2.0, 2.0), x_length=1.3*4.0, y_range=(-4.0, 1.0), y_length=1.3*5.0).shift(0.5*DOWN).set_opacity(0.3)

# CUSTOM MOBJECTS

class DoublePendelum(VGroup):
    def __init__(self, theta, phi, **kwargs):
        start_point = ax.c2p(0, 0)
        middle_point = ax.c2p(l * sin(theta), - l * cos(theta))
        end_point = ax.c2p(l * sin(theta) + l * sin(phi), - l * cos(theta) - l * cos(phi))

        first_line = Line(start_point, middle_point)
        second_line = Line(middle_point, end_point)

        first_dot = Dot(middle_point)
        second_dot = Dot(end_point)

        super().__init__(first_line, first_dot, second_line, second_dot, **kwargs)

class MotionTracker(ParametricFunction):
    def __init__(self, theta, phi, t_end, **kwargs):
        delta_t = 1.5
        t_start = t_end - delta_t if t_end > delta_t else 0.0
        super().__init__(
            lambda t: ax.c2p(l * sin(theta(t)) + l * sin(phi(t)), - l * cos(theta(t)) - l * cos(phi(t))),
            t_range=(t_start, t_end),
            **kwargs
        )



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

# numerics
first_ode = DoublePendelumNumerics(theta_0=first_theta_0, phi_0=first_phi_0, sim_time=sim_time)
first_theta = first_ode.get_theta_solution()
first_phi = first_ode.get_phi_solution()

second_ode = DoublePendelumNumerics(theta_0=second_theta_0, phi_0=second_phi_0, sim_time=sim_time)
second_theta = second_ode.get_theta_solution()
second_phi = second_ode.get_phi_solution()

# updaters for pendelums
t = ValueTracker(0.0)

first_pendelum = DoublePendelum(first_theta(t.get_value()), first_phi(t.get_value())).set_color(first_color)
first_pendelum_copy = first_pendelum.copy()
first_pendelum.add_updater(lambda mob: mob.become(
    DoublePendelum(first_theta(t.get_value()), first_phi(t.get_value())).set_color(first_color)    
))
first_tracker = MotionTracker(first_theta, first_phi, t.get_value(), color=first_color)
first_tracker.add_updater(lambda mob: mob.become(
    MotionTracker(first_theta, first_phi, t.get_value(), color=first_color)
))

second_pendelum = DoublePendelum(second_theta(t.get_value()), second_phi(t.get_value())).set_color(second_color)
second_pendelum.add_updater(lambda mob: mob.become(
    DoublePendelum(second_theta(t.get_value()), second_phi(t.get_value())).set_color(second_color)
))
second_tracker = MotionTracker(second_theta, second_phi, t.get_value(), color=second_color)
second_tracker.add_updater(lambda mob: mob.become(
    MotionTracker(second_theta, second_phi, t.get_value(), color=second_color)
))

title = Tex(r"\textbf{$\mathbb{B}$", r"utterfly effect.}", height=0.7).move_to(5*UP)
title[0].set_color(title_color)

# SCENE

class ButterflyEffectScene(Scene):
    def construct(self):
        self.add(ax, first_pendelum, first_pendelum_copy, first_tracker, second_tracker, title)
        self.play(ReplacementTransform(first_pendelum_copy, second_pendelum), run_time=1.5)
        self.play(t.animate.set_value(sim_time), run_time=sim_time, rate_func=linear)
        self.wait()
