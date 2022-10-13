from typing import List
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import NumericProperty, ListProperty


Builder.load_string(
    """

<Ball>
    size_hint: None, None
    size: root.ball_size, root.ball_size

    canvas.before:
        Color:
            rgba: root.ball_color

        Ellipse:
            size: self.size
            pos: self.pos



    """
)


class Ball(BoxLayout):
    ball_size = NumericProperty("20dp")
    ball_color = ListProperty([1, 1, 1, 1])
