from config import *

class EigenClock(VGroup):
    def __init__(self, A, theta):
        super().__init__()
        self.A = A
        self.theta = theta

        self.vector = Arrow(start=ax.c2p(0, 0), end=ax.c2p(*self.get_vector(self.theta)), buff=0.0, color=vector_color)
        self.matrix_vector = Arrow(start=ax.c2p(0, 0), end=ax.c2p(*self.get_matrix_vector(self.theta)), buff=0.0, color=matrix_color)
        self += self.vector
        self += self.matrix_vector

        self += self.get_label(self.vector, "v").set_color(vector_color)
        self += self.get_label(self.matrix_vector, "A v").set_color(matrix_color)

        self += ParametricFunction(lambda phi: ax.c2p(*self.get_vector(phi)), t_range=(0, self.theta), color=vector_color)
        self += ParametricFunction(lambda phi: ax.c2p(*self.get_matrix_vector(phi)), t_range=(0, self.theta), color=matrix_color)

    def get_vector(self, theta):
        return cos(theta), sin(theta)
    
    def get_matrix_vector(self, theta):
        return tuple(self.A @ array(self.get_vector(theta)))
    
    def get_label(self, vector, tex):
        eps = 0.4
        rotated_vector = vector.copy().rotate(-45*DEGREES)
        direction = rotated_vector.get_end() - rotated_vector.get_start()
        direction = eps * direction / norm(direction)
        return MathTex(tex).move_to(vector.get_end() + direction)
    
    def get_eigenvalue_visual(self, abs_eigenvalue):
        rotated_matrix_vector = self.matrix_vector.copy().rotate(90*DEGREES)
        direction = rotated_matrix_vector.get_end() - rotated_matrix_vector.get_start()
        direction = direction / norm(direction)
        double_arrow = DoubleArrow(start=self.matrix_vector.get_start(), end=self.matrix_vector.get_end(), buff=0.0, color=eigen_color).shift(0.25*direction)
        label = MathTex(abs_eigenvalue, color=eigen_color).next_to(double_arrow.get_center(), direction, buff=0.1)
        return VGroup(double_arrow, label)


vector_color = "#74ee15"     # green
matrix_color = "#f000ff"     # pink
eigen_color = "#4deeea"     # blueish

title = Tex(r"\textbf{$\mathbb{E}$igenvectorclock.}").scale(1.25).set_color([vector_color, WHITE]).shift(4.5*UP)

ax = Axes(
    x_range=(-2, 2),
    x_length=7,
    y_range=(-2, 2),
    y_length=7
)
ax.x_axis.add_numbers({1: "1"})
ax.y_axis.add_numbers({1: "1"})

A = array([
    [1/2, 3/2],
    [3/2, 1/2]
])

theta = ValueTracker(0.0)

clock = EigenClock(A, theta.get_value())
clock.add_updater(lambda mob: mob.become(EigenClock(A, theta.get_value())))

degrees = [45*DEGREES, 135*DEGREES, 225*DEGREES, 315*DEGREES]
abs_eigenvalues = ["2", "1", "2", "1"]
eigenvalues = ["2", "-", "2", "-"]
run_times = [2.5, 2.0, 1.5, 1.5]

class EigenVectorClockScene(Scene):
    def construct(self):
        #self.add(ax)
        self.play(Write(title), run_time=1.0)
        self.play(FadeIn(ax, run_time=1.5), Create(clock))
        
        for degree, abs_eigenvalue, eigenvalue, run_time in zip(degrees, abs_eigenvalues, eigenvalues, run_times):
            self.play(theta.animate.set_value(degree), run_time=run_time)

            eigen_line = DashedLine(-2.5*clock.vector.get_end(), 2.5*clock.vector.get_end())
            eigen_visual = clock.get_eigenvalue_visual(abs_eigenvalue)
            eigen_equation = MathTex("A v", "=", eigenvalue, "v").scale(1.3).shift(3.5*DOWN)
            eigen_equation[0].set_color(matrix_color)
            eigen_equation[2].set_color(eigen_color)
            eigen_equation[3].set_color(vector_color)
            background = SurroundingRectangle(eigen_equation, buff=0.4, fill_color=BLACK, fill_opacity=1, stroke_color=GREY)

            self.play(FadeIn(eigen_line))
            self.play(Create(eigen_visual), run_time=0.5)
            self.play(Create(background), Write(eigen_equation))
            self.wait(1.5)
            self.play(FadeOut(eigen_visual), FadeOut(eigen_line), FadeOut(eigen_equation), FadeOut(background))
            

        self.play(theta.animate.set_value(360*DEGREES), run_time=1.5)
        clock.clear_updaters()
        self.play(FadeOut(clock), FadeOut(ax), FadeOut(title))
        self.wait()