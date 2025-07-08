from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label


class CommonCheckbox(BoxLayout):
    def __init__(self, text: str, default_value: False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (1.0, None)
        self.height = 35
        self.add_widget(Label(text=text))
        checkbox = CheckBox()
        checkbox.active = default_value
        self.add_widget(checkbox)
        self.checkbox = checkbox

    def bind(self, active):
        self.checkbox.bind(active=active)

    def is_active(self) -> bool:
        return self.checkbox.active