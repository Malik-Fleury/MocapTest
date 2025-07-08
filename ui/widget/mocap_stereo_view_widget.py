from kivy.uix.boxlayout import BoxLayout

from logic.stereo_cameras import StereoCameras
from ui.widget.mocap_view_widget import MocapViewWidget


class MocapStereoViewWidget(BoxLayout):
    def __init__(self, stereo_camera: StereoCameras,  **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.mocap_left_view = MocapViewWidget(stereo_camera.get_left_camera())
        self.mocap_right_view = MocapViewWidget(stereo_camera.get_right_camera())
        self.add_widget(self.mocap_left_view)
        self.add_widget(self.mocap_right_view)

    def get_mocap_left_view(self) -> MocapViewWidget:
        return self.mocap_left_view

    def get_mocap_right_view(self) -> MocapViewWidget:
        return self.mocap_right_view

    def release(self):
        self.mocap_left_view.release()
        self.mocap_right_view.release()