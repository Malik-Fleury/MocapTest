from kivy.graphics import Color, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

class LogWidget(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll_layout = BoxLayout(padding=15, orientation='vertical', size_hint_x=1, size_hint_y=None, spacing=5)
        self.add_widget(self.scroll_layout)
        with self.canvas.after:
            Color(1, 1, 1, 1)
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)
        self.bind(pos=self.update_border, size=self.update_border)
        self.scroll_layout.bind(minimum_height=self.scroll_layout.setter('height'))

    def update_border(self, *args):
        self.border.rectangle = (self.x, self.y, self.width, self.height)

    def update_label_size(self, *args):
        self.log_label.text_size = (self.log_label.width, None)
        self.log_label.height = self.log_label.texture_size[1]

    def add_log_entry(self, log: str):
        label = Label(
            text=log,
            size_hint_x=1,
            size_hint_y=None,
            height=20,
            halign="left",
            valign="top",
        )
        label.bind(size=self.update_text_size)
        self.scroll_layout.add_widget(label)

    def update_text_size(self, instance, size):
        """ Trick to set the text to left """
        instance.text_size = (instance.width, None)