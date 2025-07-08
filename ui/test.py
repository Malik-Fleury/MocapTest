from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button


class ScrollApp(App):
    def build(self):
        # Création d'un BoxLayout vertical
        self.box_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,  # Permet au BoxLayout de dépasser en hauteur
            spacing=5
        )
        self.box_layout.bind(minimum_height=self.box_layout.setter('height'))  # Ajuster la hauteur dynamiquement

        # ScrollView contenant le BoxLayout
        self.scroll_view = ScrollView(size_hint=(1, 0.8))
        self.scroll_view.add_widget(self.box_layout)

        # Bouton pour ajouter des Labels dynamiques
        add_button = Button(text="Add Label", size_hint=(1, 0.1))
        add_button.bind(on_press=self.add_label)

        # Mise en page principale
        main_layout = BoxLayout(orientation="vertical")
        main_layout.add_widget(self.scroll_view)
        main_layout.add_widget(add_button)

        return main_layout

    def add_label(self, instance):
        """Ajoute un Label dynamique aligné à gauche."""
        label = Label(
            text=f"Log {len(self.box_layout.children) + 1}: This is a log entry.",
            size_hint=(1, None),  # Occupe toute la largeur (x), hauteur fixe (y)
            height=50,            # Hauteur fixe
            halign="left",        # Alignement du texte à gauche
            valign="middle"       # Alignement vertical au centre
        )
        label.bind(size=self.update_text_size)  # Met à jour text_size pour forcer l'alignement
        self.box_layout.add_widget(label)

    def update_text_size(self, instance, size):
        """Met à jour text_size pour aligner correctement le texte à gauche."""
        instance.text_size = (instance.width, None)


if __name__ == "__main__":
    ScrollApp().run()