from kivy.uix.textinput import TextInput


class DecimalInput(TextInput):
    def __init__(self, default_value = False, **kwargs):
        super().__init__(**kwargs)
        self.disabled = not default_value
        self.multiline = False
        self.size_hint = (1, None)
        self.size = (0, 35)

    def insert_text(self, substring, from_undo=False):
        allowed_chars = "0123456789."
        if substring not in allowed_chars:
            return
        if '.' in self.text and substring == '.':
            return
        return super().insert_text(substring, from_undo=from_undo)

    def is_empty(self):
        return self.text == ''