from kivy import Config
from kivy.app import App

from ui.screen.mocap_screen import MocapMainScreen

Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '650')

class MocapApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = None

    def build(self):
        self.main_screen = MocapMainScreen()
        return self.main_screen

    def on_stop(self):
        self.main_screen.release()

if __name__ == "__main__":
    MocapApp().run()