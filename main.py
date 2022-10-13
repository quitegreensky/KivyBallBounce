from kivy.app import App
from kivy.lang import Builder
from cls.field import MainField

kv = """

Screen:


    MainField:
        border_width: dp(10)
        border_color: 0.3, 0.1, 1, 1





"""

class MainApp(App):

    def build(self):
        self.main_kv = Builder.load_string(kv)
        return self.main_kv


MainApp().run()
