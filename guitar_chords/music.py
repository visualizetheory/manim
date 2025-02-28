from config import *

# colors
color_E = "#fe0000"     # red
color_A = "#FF8800"     # orange
color_D = "#ffe700"     # yellow
color_G = "#f000ff"     # pink
color_B = "#4deeea"     # blueish
color_e = "#74ee15"     # green

# axes
ax = ThreeDAxes(
    x_range=(-1.0, 5.0), 
    y_range=(-1, 1), 
    z_range=(-1, 1), 
).set_opacity(0.0)
labels = ax.get_axis_labels(
    x_label=Tex("$x$"),
    y_label=Tex("$y$").rotate(-90*DEGREES),
    z_label=Tex("$z$"),
).set_opacity(0.0)

class StringMath():
    '''
    Math for guitar string of length [L] and propagation speed [c]. Computes solution of wave equation
    with initial deflection [initial_func] using a fourierseries of order [order].
    '''
    def __init__(self, initial_func, L=PI, c=1.0, order=1, gamma=0.0):
        self.initial_func = initial_func
        self.L = L
        self.c = c
        self.order = order
        self.gamma = gamma
        self.fourier_coeff = self.compute_fourier_coeff()

    def compute_fourier_coeff(self):
        coefficients = {}
        for k in range(1, self.order + 1):
            coefficients[k] = ( 2 / self.L ) * integrate.quad(lambda x: sin( PI * k * x / self.L ) * self.initial_func(x), 0, self.L)[0]
        return coefficients

    @classmethod
    def get_string(cls, d, m=1.0, L=PI, c=1.0, order=1, gamma=0.0):
        '''
        Construcs string with displacement [d] from the right side. [m] is the maximum of the displacement.
        '''
        initial_func_1 = lambda x: m * x / ( L - d ) if x <= L - d else - ( m / d ) * ( x - L ) 
        eps = 0.2 * L 
        def initial_func_2(x):
            if x <= L - d - eps:
                return 0
            elif L - d - eps < x <= L - d:
                return m * ( x - ( L - d - eps ) ) / eps
            elif L - d < x <= L - d + eps:
                return - ( m / eps ) * x + ( m / eps ) * ( L - d + eps )
            else:
                return 0
        return cls(initial_func_1, L=L, c=c, order=order, gamma=gamma)

    def get_function(self, t=0.0):
        '''
        Returns string at time [t]. 
        '''
        return lambda x: sum([
            self.fourier_coeff[k] * cos( PI * k * self.c * t / self.L ) * sin(PI * k * x / self.L ) * exp( - self.gamma * t**2 )
             for k in self.fourier_coeff
        ])


class ChordMath():
    '''
    Construct chords from fret dictionary [fret_dict].
    '''
    def __init__(self, fret_dict, L, d, c=1.0, order=1, m=1.0, gamma=0.0):
        self.L = L
        self.fret_dict = fret_dict
        c_dict = {
            'E' : c,
            'A' : 2**( 5 / 12 ) * c,
            'D' : 2**( 10 / 12 ) * c,
            'G' : 2**( 15 / 12 ) * c,
            'B' : 2**( 19 / 12 ) * c,
            'e' : 2**( 24 / 12 ) * c
        }
        string_dict = {
            letter: StringMath.get_string(
                d, 
                m=m, 
                L=L - self.get_fret(fret_dict[letter]), 
                c=c_dict[letter], 
                order=order,
                gamma=gamma,
            ) for letter in fret_dict
        }
        self.string_dict = string_dict
    
    def get_fret(self, n): # positon of [n]-th fret
        return self.L * ( 1 - 2**( - n / 12 ) )

    @classmethod 
    def get_chord(cls, name, L, d, **kwargs):
        match name:
            case 'Em':
                fret_dict = {
                    'E' : 0,
                    'A' : 2,
                    'D' : 2,
                    'G' : 0,
                    'B' : 0,
                    'e' : 0,
                }
            case 'G':
                fret_dict = {
                    'E' : 3,
                    'A' : 2,
                    'D' : 0,
                    'G' : 0,
                    'B' : 0,
                    'e' : 3,
                }
            case 'D':
                fret_dict = {
                    'D' : 0,
                    'G' : 2,
                    'B' : 3,
                    'e' : 2,
                }
            case 'A':
                fret_dict = {
                    'A' : 0,
                    'D' : 2,
                    'G' : 2,
                    'B' : 2,
                    'e' : 0,
                }
        return cls(fret_dict, L, d, **kwargs)


class ChordVisual(VGroup):
    '''
    Visual representation of chord at time [t]. 
    '''
    def __init__(self, chord, t=0.0):
        super().__init__()
        color_dict = {
            'E' : color_E,
            'A' : color_A,
            'D' : color_D,
            'G' : color_G,
            'B' : color_B,
            'e' : color_e,
        }
        
        delta = 0.085 #0.045
        shift = 0.25
        z = 5 * delta + shift
        for letter, string in chord.string_dict.items():
            fret_location = chord.get_fret(chord.fret_dict[letter])
            string_length = chord.L
            function = lambda x: string.get_function(t=t)(x - fret_location)
            self += Dot(ax.c2p(fret_location, 0, z), fill_opacity=1.0, color=color_dict[letter], radius=0.06).rotate(90 * DEGREES, RIGHT)
            self += ParametricFunction(
                lambda t: ax.c2p(t, function(t), z), 
                t_range=(fret_location, string_length), 
                color=color_dict[letter]
            )
            self += Dot(ax.c2p(string_length, 0, z), fill_opacity=1.0, color=color_dict[letter], radius=0.06).rotate(90 * DEGREES, RIGHT)
            z -= delta

class ChordNotes(VGroup):
    '''
    Show notes in dictionary [note_dict] with sharps indicated in the list [hashtags].
    '''
    def __init__(self, note_dict, aux_lines, label, hashtags):
        super().__init__()
        base = array([-2, -4.32, 0]) # coords of note E
        delta = 0.185                # distance between two vertical lines
        radius = 0.09
        color_dict = {
            'E' : color_E,
            'A' : color_A,
            'D' : color_D,
            'G' : color_G,
            'B' : color_B,
            'e' : color_e,
        }
        self += Tex(label).move_to(base + 7 * delta * UP)
        for line in aux_lines:
            epsilon = 0.15
            self += Line(base - epsilon * RIGHT + line * delta * UP, base + epsilon * RIGHT + line * delta * UP)
        for letter in note_dict:
            self += Circle(color=color_dict[letter], radius=radius, fill_opacity=0.4).move_to(base + note_dict[letter] * delta * UP)
        for h in hashtags:
            shift = 0.3
            self += Tex(r'\#').scale(0.8).move_to(base + h * delta * UP - shift * RIGHT)

    @classmethod
    def get_chord(cls, name):
        match name:
            case 'Em':
                note_dict = {
                    'E' : -3.5,
                    'A' : -1.5,
                    'D' : 0.0,
                    'G' : 1.0,
                    'B' : 2.0, 
                    'e' : 3.5,
                }
                aux_lines = [-1.0, -2.0, -3.0]
                label = "E minor"
                hashtags = []
            case 'G':
                note_dict = {
                    'E' : -2.5,
                    'A' : -1.5,
                    'D' : -0.5,
                    'G' : 1.0,
                    'B' : 2.0,
                    'e' : 4.5,
                }
                aux_lines = [-1.0, -2.0]
                label = 'G major'
                hashtags = []
            case 'D':
                note_dict = {
                    'D' : -0.5,
                    'G' : 1.5,
                    'B' : 3.0,
                    'e' : 4.0
                }
                aux_lines = []
                label = 'D major'
                hashtags = [4.0]
            case 'A':
                note_dict = {
                    'A' : -2.0,
                    'D' : 0.0,
                    'G' : 1.5,
                    'B' : 2.5,
                    'e' : 3.5,
                }
                aux_lines = [-1.0, -2.0]
                label = 'A major'
                hashtags = [2.5]
        return cls(note_dict, aux_lines, label, hashtags)

class Music(ThreeDScene):
    '''
    Animate guitar chords.
    '''
    def construct(self):
        L = 4.0
        d = 0.5
        c = 1.5
        m = 0.6
        order = 2
        gamma = 0.125
        sim_time = 5.0

        title = Tex(r"\textbf{$\mathbb{G}$uitar chords.}").scale(1.35).set_color([color_B, WHITE]).shift(5*UP)
        sheet = ImageMobject("music_sheet.png").scale(0.35).shift(4*DOWN)

        t = ValueTracker(0.0)

        math = ChordMath.get_chord('Em', L, d, order=order, c=c, m=m, gamma=gamma)
        visual = ChordVisual(math)
        notes = ChordNotes.get_chord('Em')
        visual.add_updater(lambda mob: mob.become(
            ChordVisual(math, t=t.get_value())    
        ))
        self.set_camera_orientation(phi=60*DEGREES, theta=-175*DEGREES)
        self.begin_ambient_camera_rotation(rate=0.175)
        self.add_fixed_in_frame_mobjects(title, sheet, notes)
        self.remove(title, notes, sheet)
        self.add(ax, labels)
        self.play(Write(title, run_time=1.5), FadeIn(sheet, run_time=1.5), Create(notes, run_time=2.5), Create(visual, run_time=2.5))
        self.wait(0.5)
        self.play(t.animate(run_time=sim_time).set_value(sim_time), rate_func=linear)
        self.play(FadeOut(notes, run_time=0.5))
        visual.clear_updaters()
        
        for name in ['G', 'D', 'A']:
            next_math = ChordMath.get_chord(name, L, d, order=order, c=c, m=m, gamma=gamma)
            next_visual = ChordVisual(next_math)
            next_notes = ChordNotes.get_chord(name)
            self.add_fixed_in_frame_mobjects(next_notes)
            self.remove(next_notes)
            self.play(
                ReplacementTransform(visual, next_visual, run_time=2.0), 
                Create(next_notes, run_time=1.0),
            )
            self.wait(0.5)
            t.set_value(0.0)
            next_visual.add_updater(lambda mob: mob.become(
                ChordVisual(next_math, t=t.get_value())
            ))
            self.play(t.animate(run_time=sim_time).set_value(sim_time), rate_func=linear)
            self.play(FadeOut(next_notes, run_time=0.5))
            next_visual.clear_updaters()
            visual = next_visual
        self.wait(1.0)


