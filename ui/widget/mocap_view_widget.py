from threading import Thread

import cv2
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

from logic.camera import Camera

class MocapViewWidget(BoxLayout):
    def __init__(self, camera: Camera, on_update_image_callback = None, **kwargs):
        super().__init__(**kwargs)
        self.on_update_image_callback = on_update_image_callback
        self.orientation = 'vertical'
        self.camera = camera
        self.image = Image(source=r"E:\Users\malik\Documents\Projects\NoGit\Python\MediapipeTest\images\device_not_found.jpg")
        self.label = Label(
            text=self.camera.get_camera_name(),
            font_size=20,
            size=(0,30),
            size_hint=(1, None),
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.label)
        self.add_widget(self.image)
        Thread(target=self.initialize_camera, daemon=True).start()
        Clock.schedule_interval(self.update_image, 1.0 / self.camera.get_fps())

    def initialize_camera(self):
        self.camera.start()

    def update_image(self, delta_time: float):
        if self.camera.is_started() and self.camera.is_frame_available():
            frame = self.camera.get_shared_frame()
            if self.on_update_image_callback is not None:
                self.on_update_image_callback(frame, delta_time)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, _ = frame.shape
            texture = Texture.create(size=(width, height), colorfmt="rgb")
            texture.blit_buffer(frame.tobytes(), colorfmt="rgb", bufferfmt="ubyte")
            texture.flip_vertical()
            self.label.text = self.camera.get_camera_name() + " (" + str(self.camera.get_fps_stats()) + ")"
            self.image.texture = texture

    def set_on_update_image_callback(self, on_update_image_callback):
        self.on_update_image_callback = on_update_image_callback

    def release(self):
        self.camera.stop()