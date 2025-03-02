from config import *

# CUSTOM MOBJECTS

class CoordinateSystem(VGroup):
    '''
    Custom coordinate system. 
    '''
    def __init__(self):
        super().__init__()
        self += ax
        self.add_labels()
    
    def add_labels(self):
        self += MathTex("x", color=x_color, stroke_width=2).next_to(p(1.2, 0), LEFT + UP, buff=0.25)
        x_dot = Dot(p(1, 0), color=ax_color, radius=0.1)
        x_dot.z_index = 1
        self += x_dot
        self += MathTex("1", stroke_width=2, color=ax_color).next_to(p(1.0075, 0), RIGHT, buff=0.5)
        y_label = MathTex("y", stroke_width=2.5, color=y_color).next_to(p(0, 0.25), UP, buff=0.35)
        background = Square(side_length=0.7, fill_color=BLACK, fill_opacity=1, stroke_color=GREY).move_to(y_label)
        self += background
        self += y_label
        self += MathTex("-1", stroke_width=2.5, color=ax_color).next_to(p(0, -0.95), UP)
        self += Dot(p(0, -1), color=ax_color, radius=0.1)


class Frets():
    '''
    Visualization for fretboard.
    '''
    def __init__(self):
        self.number = 12
        self.x_dots = [self.get_x_dot(n) for n in range(1, self.number + 1)]
        self.x_dot_labels = [self.get_x_dot_label(n) for n in range(1, self.number + 1)]
        self.y_dots = [self.get_y_dot(n) for n in range(1, self.number + 1)]
        self.y_dot_labels = [self.get_y_dot_label(n) for n in range(1, self.number + 1)]
        self.horizontal_lines = [self.get_horizontal_line(n) for n in range(1, self.number + 1)]
        self.vertical_lines = [self.get_vertical_line(n) for n in range(1, self.number + 1)]

    def get_x_dot(self, n):
        dot = Dot(p(self.pos(n), 0), color=x_color, radius=0.1)
        dot.z_index = 1
        return dot
    
    def get_x_dot_label(self, n):
        return MathTex(f"2^{{-\\frac{{{n}}}{{12}}}}", color=x_color, stroke_width=2).next_to(p(self.pos(n), 0), LEFT, buff=0.5).scale(1.1)

    def get_y_dot(self, n):
        return Dot(p(0, log2(self.pos(n))), color=y_color, radius=0.1)
    
    def get_y_dot_label(self, n):
        label = MathTex(f"-\\frac{{{n}}}{{12}}", color=y_color, stroke_width=2.5).next_to(p(0, log2(self.pos(n)) + 0.035), DOWN, buff=0.4).scale(0.9)
        background = Square(side_length=1.3, fill_color=BLACK, fill_opacity=1, stroke_color=GREY).move_to(label)
        return VGroup(background, label)
    
    def get_horizontal_line(self, n):
        return Line(p(self.pos(n), 0), p(self.pos(n), log2(self.pos(n))), color=ax_color, stroke_width=4)
    
    def get_vertical_line(self, n):
        return Line(p(self.pos(n), log2(self.pos(n))), p(0, log2(self.pos(n))), color=ax_color, stroke_width=4)

    @staticmethod
    def pos(n):
        return 2**(-n/12)


# colors
x_color = "#2CFA02" # green
y_color = "#00f6ff" # orange
ax_color = RED
log_color = WHITE

# axes (global)
ax = Axes(x_range=(-0.2, 1.2), y_range=(-1.2, 0.2), axis_config={"color": ax_color, "stroke_width": 7}).rotate(90*DEGREES)
p = ax.c2p # shorthand

# guitar image
guitar = ImageMobject("guitar.png").scale(1.405).shift(2.18*LEFT).shift(0.31*DOWN)

# coordinate system
coord_system = CoordinateSystem()

# title
title = Tex(r"$\mathbb{B}$uilding the guitar.").scale(1.1).rotate(90*DEGREES).next_to(p(0.7, 0), LEFT, buff=0.5)

# log graph
log_graph = ax.plot(log2, x_range=(0.3, 2), color=log_color)
log_label = MathTex(r"\log_2", "x",  "=", "y", stroke_width=2).move_to(p(0.8, -0.7))
log_label[1].set_color(x_color)
log_label[3].set_color(y_color)

# fretboard
frets = Frets()

# octave
x_octave_label = MathTex(r"\frac{1}{2}", color=x_color, stroke_width=2).next_to(p(1/2, 0), LEFT, buff=0.5)
octave_tex = Tex("octave", color=x_color, stroke_width=2).next_to(p(1/2, 0), LEFT, buff=0.5)

# uniform steps
uniform = VGroup()
tex = Tex(r"uniform\,", "steps", r"\,on", "logarithmic scale", stroke_width=2).align_to(p(0, -1/12), LEFT).align_to(p(-0.1, 0), DOWN)
tex[1].set_color(y_color)
tex[3].next_to(tex[0], DOWN + RIGHT).shift(1.1*LEFT)
box = SurroundingRectangle(tex, buff=0.2, fill_color=BLACK, fill_opacity=1, stroke_color=GREY)
uniform += box
uniform += tex


# SCENE
class Fretboard(MovingCameraScene):
    def construct(self):
        self.intro()
        self.show_frets()
        #self.summary()

    def intro(self):
        '''
        Show title and rotate guitar.
        '''
        self.camera.frame.save_state()
        self.camera.frame.shift(2*LEFT)
        self.camera.frame.set(width=5)
        rotation_angle = 30*DEGREES
        guitar_and_title = Group(guitar, title).rotate(-rotation_angle)
        self.add(guitar)
        self.play(Write(title))
        self.wait()
        self.play(Rotate(guitar_and_title, rotation_angle), Restore(self.camera.frame))

    def show_frets(self):
        '''
        Construct fretboard and show log scale.
        '''
        self.play(ReplacementTransform(title, coord_system))
        self.play(Create(log_graph), Write(log_label))
        self.play(Write(frets.x_dot_labels[0]), Create(frets.x_dots[0]))
        self.play(Create(frets.horizontal_lines[0]), run_time=0.5)
        self.play(Create(frets.vertical_lines[0]), run_time=0.5)
        self.play(Write(frets.y_dot_labels[0]), Create(frets.y_dots[0]))
        for n in range(1, frets.number):
            run_time = 0.5**n if n <= 3 else 0.5**3 if 3 < n < 9 else 0.5**2 if 9 <= n < 12 else 0.5
            self.play(ReplacementTransform(frets.x_dot_labels[n-1], frets.x_dot_labels[n]), Create(frets.x_dots[n]), run_time=run_time)
            self.play(Create(frets.horizontal_lines[n]), run_time=run_time)
            self.play(Create(frets.vertical_lines[n]), run_time=run_time)
            self.play(Create(frets.y_dots[n]), ReplacementTransform(frets.y_dot_labels[n-1], frets.y_dot_labels[n]), run_time=run_time) 

    def summary(self):
        '''
        Label octave and summarize.
        '''
        self.play(ReplacementTransform(frets.x_dot_labels[-1], x_octave_label))
        self.wait(0.5)
        self.play(ReplacementTransform(x_octave_label, octave_tex))
        self.wait(0.5)
        self.play(ReplacementTransform(frets.y_dot_labels[-1], uniform))
        self.wait(3)
