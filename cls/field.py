
from tkinter.tix import Tree
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.properties import NumericProperty, ListProperty
from cls.ball import Ball
from functools import partial
from kivy.animation import Animation
from kivy.vector import Vector



Builder.load_string(
    """
<MainField>

    canvas.before:

        Color:
            rgba: root.border_color

        Rectangle: # left
            pos: self.pos
            size: root.border_width, self.height

        Rectangle: # top
            pos: self.x, self.top - root.border_width
            size: self.width, root.border_width

        Rectangle: # right
            pos: self.right - self.border_width, self.y
            size: root.border_width, self.height

        Rectangle: # bottom
            pos: self.pos
            size: self.width, root.border_width


""")


class MainField(FloatLayout):
    border_color = ListProperty([1, 0, 1, 1])
    border_width = NumericProperty("30dp")
    ball_size = NumericProperty("50dp")
    speed = NumericProperty("0.2") #seconds per 100px

    initial_pos = []
    last_pos = []
    ball = None
    dynamic_speed = None
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


    def prepare_scene(self, touch):
        self.clear_widgets()
        ball_x = touch.x - self.ball_size/2
        ball_y = touch.y - self.ball_size/2
        self.ball = Ball(ball_size=self.ball_size, pos=[ball_x, ball_y])
        self.add_widget(self.ball)

    def on_touch_down(self, touch):
        if self.ball:
            Animation.cancel_all(self.ball)
        self.prepare_scene(touch)
        self.initial_pos = touch.pos


    def on_touch_up(self, touch):
        dx, dy = self.initial_pos
        x, y = touch.pos
        distance = Vector(self.initial_pos).distance(touch.pos)
        if distance==0:
            return True
        self.dynamic_speed = (100/distance)*self.speed
        collision_point = self.get_collision_point([dx, dy], [x, y])
        bounce_point = self.get_bounce_collision_point(collision_point[0], collision_point[1], [dx, dy])
        self.move_ball_anim(collision_point, bounce_point)

    def move_ball_anim(self, collision_point, bounce_point):
        wall = collision_point[1]
        x, y = collision_point[0]
        x_buffer = 0
        y_buffer = 0
        if wall=="t":
            y_buffer = -self.ball_size
        if wall=="r":
            x_buffer = -self.ball_size
        if wall=="b":
            y_buffer = 0
        if wall=="l":
            x_buffer = 0

        dis = Vector(collision_point[0]).distance(self.ball.pos)
        t = (dis/100)*self.dynamic_speed
        next_bounce_point = self.get_bounce_collision_point(bounce_point[0], bounce_point[1], collision_point[0])
        anim = Animation(pos = [x+x_buffer, y+y_buffer], d= t)
        anim.bind(on_complete=lambda *args: self.move_ball_anim(bounce_point, next_bounce_point))
        anim.start(self.ball)

    def get_collision_point(self, p1, p2):
        x, y = p2
        dx, dy = p1

        line = partial( self.two_line_intersection, [x, y], [dx, dy] )
        initial_dir= None
        if x>dx:
            if y>dy:
                initial_dir = "tr"
            else:
                initial_dir = "lr"
        else:
            if y>dy:
                initial_dir = "tl"
            else:
                initial_dir = "ll"

        field_cords = self.get_main_field_pos()
        collision_point = None
        collision_wall = None

        intersection_r = line(field_cords["tr"], field_cords["lr"])
        intersection_t = line(field_cords["tr"], field_cords["tl"])
        intersection_b = line(field_cords["ll"], field_cords["lr"])
        intersection_l = line(field_cords["ll"], field_cords["tl"])

        if initial_dir=="tr":
            if intersection_r[1] < field_cords["tr"][1]:
                collision_point = intersection_r
                collision_wall = "r"
            else:
                collision_point = intersection_t
                collision_wall = "t"

        if initial_dir=="lr":
            if intersection_r[1] > field_cords["lr"][1]:
                collision_point = intersection_r
                collision_wall = "r"
            else:
                collision_point = intersection_b
                collision_wall = "b"

        if initial_dir=="ll":
            if intersection_l[1] > field_cords["ll"][1]:
                collision_point = intersection_l
                collision_wall = "l"
            else:
                collision_point = intersection_b
                collision_wall = "b"

        if initial_dir=="tl":
            if intersection_l[1] < field_cords["tl"][1]:
                collision_point = intersection_l
                collision_wall = "l"
            else:
                collision_point = intersection_t
                collision_wall = "t"

        return [collision_point, collision_wall]

    def get_bounce_collision_point(self, collision_point, collision_wall, dpoint):
        dx, dy = dpoint
        second_point = []
        diff_x = collision_point[0] - dx
        diff_y = collision_point[1] - dy
        if collision_wall=="t" or collision_wall=="b":
            second_point = [collision_point[0] + diff_x, dy]
        elif collision_wall=="r" or collision_wall=="l":
            second_point = [dx, collision_point[1]+ diff_y]

        new_collision_point = self.get_collision_point(collision_point, second_point)
        return new_collision_point


    def get_main_field_pos(self):
        return {
            "ll": [self.x + self.border_width, self.y + self.border_width],
            "tl": [self.x + self.border_width, self.top - self.border_width],
            "tr": [self.right - self.border_width, self.top - self.border_width],
            "lr": [self.right - self.border_width, self.y + self.border_width],
        }

    def two_line_intersection(self, p0, p1, p2, p3):
        try:
            m1 = (p1[1] - p0[1])/(p1[0] - p0[0])
        except:
            m1 = 10000000000
        try:
            m2 = (p3[1] - p2[1]) / (p3[0] - p2[0])
        except:
            m2 = 10000000000
        try:
            x = (p2[1] + m1*p0[0] - p0[1] - m2*p2[0]) / (m1-m2)
            y = m1*x - m1*p0[0] + p0[1]
        except ZeroDivisionError:
            return(0,0)

        return (x, y)