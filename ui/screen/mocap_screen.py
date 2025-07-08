from threading import Thread
from time import sleep

import cv2
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from data.math.point_2d import Point2D
from logic.calibrator import Calibrator
from logic.camera import Camera
from data.chessboard_data import ChessboardData
from logic.filesystem import ImagesFileSystem
from logic.mocap.mocap_hands_core import MocapHandsCore
from logic.packet_builder import PacketBuilder
from logic.stereo_cameras import StereoCameras
from logic.udp_server import UdpServer
from ui.widget.common_checkbox import CommonCheckbox
from ui.widget.log_widget import LogWidget
from ui.widget.mocap_stereo_view_widget import MocapStereoViewWidget


class MocapMainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.info_label = None
        self.stereo_previews = None
        self.log_widget = None
        self.triangulate_checkbox = None
        self.kalman_widget = None
        self.interlace_mode_checkbox = None
        self.debug_2d_landmarks_checkbox = None
        self.debug_2d_kalman_checkbox = None
        self.size_hint = (1.0, 1.0)
        self.stereo_cameras = StereoCameras(
            Camera(2, 60, True),
            Camera(0, 60, True),
        )
        self.chessboard_data = ChessboardData(9, 6, 0.016)
        self.calibrator = Calibrator(self.chessboard_data)
        self.image_file_system = ImagesFileSystem(r"E:\Users\malik\Documents\Projects\NoGit\Python\MediapipeTest\images")
        self.udp_server = UdpServer('127.0.0.1', 5005)
        self.build_interface()
        self.mocap_hands_core = MocapHandsCore()

    def build_interface(self):
        left_area = self.create_left_area()
        right_area = self.create_vertical_menu()
        self.add_widget(left_area)
        self.add_widget(right_area)

    def create_left_area(self):
        vertical_layout = BoxLayout(orientation="vertical")
        stereo_previews = self.create_stereo_previews()
        info_label = self.create_info_label()
        log_widget = LogWidget()
        vertical_layout.add_widget(stereo_previews)
        vertical_layout.add_widget(log_widget)
        self.info_label = info_label
        self.stereo_previews = stereo_previews
        self.log_widget = log_widget
        self.log_widget.add_log_entry("Cameras are initializing... Please wait...")
        return vertical_layout

    def create_stereo_previews(self) -> MocapStereoViewWidget:
        stereo_previews = MocapStereoViewWidget(self.stereo_cameras)
        stereo_previews.get_mocap_left_view().set_on_update_image_callback(self.on_update_image_left_event)
        stereo_previews.get_mocap_right_view().set_on_update_image_callback(self.on_update_image_right_event)
        return stereo_previews

    def create_info_label(self) -> Label:
        info_label = Label(text='Info')
        return info_label

    def create_vertical_menu(self) -> BoxLayout:
        vertical_layout = BoxLayout(
            orientation = 'vertical',
            width = 250,
            size_hint = (None, 1.0),
            padding = 15
        )
        capture_button = self.create_common_button(text="Capture", on_press=self.on_capture_button_pressed)
        calibrate_button = self.create_common_button(text="Calibrate", on_press=self.on_calibrate_button_pressed)
        run_button = self.create_common_button(text="Run", on_press=self.on_run_button_pressed)
        sample_error_button = self.create_common_button(text="Sample Error", on_press=self.on_new_sampling)
        self.triangulate_checkbox = CommonCheckbox('Triangulation', True)
        self.interlace_mode_checkbox = CommonCheckbox('Interlace mode', True)
        self.debug_2d_landmarks_checkbox = CommonCheckbox('Debug 2D', True)
        self.debug_2d_kalman_checkbox = CommonCheckbox('Debug Kalman', True)
        vertical_layout.add_widget(capture_button)
        vertical_layout.add_widget(calibrate_button)
        vertical_layout.add_widget(run_button)
        vertical_layout.add_widget(sample_error_button)
        vertical_layout.add_widget(self.triangulate_checkbox)
        vertical_layout.add_widget(self.interlace_mode_checkbox)
        vertical_layout.add_widget(self.debug_2d_landmarks_checkbox)
        vertical_layout.add_widget(self.debug_2d_kalman_checkbox)
        vertical_layout.add_widget(Widget(size_hint=(1.0, 1.0)))
        return vertical_layout

    def create_common_button(self, text: str, on_press: callable):
        button = Button(text=text)
        button.bind(on_press=on_press)
        button.size_hint = (1.0, None)
        button.height = 35
        return button

    def on_capture_button_pressed(self, instance):
        Clock.schedule_interval(self.on_capture_timer_elapsed, 3)
        self.log_widget.add_log_entry("Capture starting in 3 seconds")
        self.counter = 0

    def on_capture_timer_elapsed(self, dt:float):
        self.log_widget.add_log_entry("Capturing...")
        result, left_frame, right_frame = self.calibrator.capture_stereo(self.stereo_cameras)
        if result:
            self.log_widget.add_log_entry("Success for iteration #" + str(self.counter + 1))
            self.image_file_system.save_image(('/' + self.stereo_cameras.get_left_camera().get_camera_name() + '/picture_' + str(self.counter) + '.jpg'), left_frame)
            self.image_file_system.save_image(('/' + self.stereo_cameras.get_right_camera().get_camera_name() + '/picture_' + str(self.counter) + '.jpg'), right_frame)
            self.counter += 1
        else:
            self.log_widget.add_log_entry("Fail for iteration #" + str(self.counter + 1) + ", try again in 3 seconds")
        if self.counter == 10:
            self.log_widget.add_log_entry("Congratulations, you have captured chessboards for calibration !")
            self.counter = 0
            Clock.unschedule(self.on_capture_timer_elapsed)

    def on_calibrate_button_pressed(self, instance):
        self.log_widget.add_log_entry("Calibrating all cameras individually...")
        Thread(target=self.calibrate_cameras_individually, daemon=True).start()

    def calibrate_cameras_individually(self):
        calibration_data_list = self.stereo_cameras.calibrate_all_cameras_individually(self.image_file_system, self.chessboard_data)
        self.calibration_stereo_data = self.stereo_cameras.calibrate_stereo_cameras(calibration_data_list)

    def on_run_button_pressed(self, instance):
        self.log_widget.add_log_entry("Mocap is running...")
        Thread(target=self.run_mocap_stereo_cameras, daemon=True).start()

    def run_mocap_stereo_cameras(self):
        mocap_hands_core = self.mocap_hands_core
        packet_builder = PacketBuilder()
        while self.stereo_cameras.is_started():
            left_frame = self.stereo_cameras.get_left_camera().get_shared_frame()
            right_frame = self.stereo_cameras.get_right_camera().get_shared_frame()
            left_cam_points_3d, right_cam_points_3d = mocap_hands_core.detects_raw_points_3d_stereo(
                left_frame,
                right_frame,
            )
            if left_cam_points_3d is not None and right_cam_points_3d is not None:
                height, width, _ = left_frame.shape
                left_cam_filtrated_points_3d, right_cam_filtrated_points_3d = mocap_hands_core.apply_filtration_trackers_2d(left_cam_points_3d, right_cam_points_3d)
                left_cam_filtrated_points_3d, right_cam_filtrated_points_3d = mocap_hands_core.convert_for_triangulation(left_cam_filtrated_points_3d, right_cam_filtrated_points_3d, Point2D(width, height))
                positions = mocap_hands_core.triangulate_raw_points(
                    left_cam_filtrated_points_3d,
                    right_cam_filtrated_points_3d,
                    self.stereo_cameras.get_left_camera().get_intrinsics_matrix(),
                    self.stereo_cameras.get_right_camera().get_intrinsics_matrix(),
                    self.calibration_stereo_data,
                )
                if positions is not None:
                    positions = mocap_hands_core.apply_filtration_tracker_3d(positions)
                    packet = packet_builder.build_hand_packet(positions)
                    self.udp_server.send(packet)
            # if left_cam_landmarks is not None and right_cam_landmarks is not None:
            #     if left_cam_landmarks.multi_hand_landmarks is not None and right_cam_landmarks.multi_hand_landmarks is not None:
            #         height,width,_ = left_frame.shape
            #         left_landmarks = left_cam_landmarks.multi_hand_landmarks[0].landmark
            #         right_landmarks = right_cam_landmarks.multi_hand_landmarks[0].landmark
            #         left_landmarks = mocap_hands_core.converts_landmarks_to_np_array(left_landmarks)
            #         right_landmarks = mocap_hands_core.converts_landmarks_to_np_array(right_landmarks)
            #         left_landmarks_3d_fake = Tools.converts_2d_points_to_3d_points(left_landmarks)
            #         right_landmarks_3d_fake = Tools.converts_2d_points_to_3d_points(right_landmarks)
            #         # left_landmarks, right_landmarks = mocap_hands_core.apply_filtration(left_landmarks_3d_fake, right_landmarks_3d_fake)
            #         positions = mocap_hands_core.triangulate_raw_points(
            #             left_landmarks,
            #             right_landmarks,
            #             self.stereo_cameras.get_left_camera().get_intrinsics_matrix(),
            #             self.stereo_cameras.get_right_camera().get_intrinsics_matrix(),
            #             self.calibration_stereo_data,
            #         )
            #         if positions is not None:
            #             packet = packet_builder.build_hand_packet(positions)
            #             self.udp_server.send(packet)

    # def run_mocap_stereo_cameras(self):
    #     mocap_core = MocapCore()
    #     packet_builder = PacketBuilder()
    #     calibration_stereo_data = self.calibration_stereo_data
    #     while self.stereo_cameras.is_started():
    #         positions = mocap_core.full_process(
    #             self.stereo_cameras.get_left_camera(),
    #             self.stereo_cameras.get_right_camera(),
    #             calibration_stereo_data)
    #         if positions is not None:
    #             filtered_position = self.multi_filters.correct_and_predict(positions)
    #             packet = packet_builder.build_hand_packet(filtered_position)
    #             self.udp_server.send(packet)

    # def on_sample_error_button_pressed(self, instance):
    #     mocap_core = MocapCore()
    #     calibration_stereo_data = self.calibration_stereo_data
    #     counter_samples = 0
    #     left_camera_landmarks_captures = []
    #     right_camera_landmarks_captures = []
    #     positions_captures = []
    #     while self.stereo_cameras.is_started() and counter_samples < 100:
    #         sleep(0.005)
    #         positions = mocap_core.full_process(
    #             self.stereo_cameras.get_left_camera(),
    #             self.stereo_cameras.get_right_camera(),
    #             calibration_stereo_data)
    #         if positions is not None:
    #             positions_captures.append(positions)
    #             counter_samples += 1
    #     self.multi_filters.initialize_filters(positions_captures, 21)
    #     print("DONE")

    def on_new_sampling(self, instance):
        mocap_hands_core = self.mocap_hands_core
        left_cam_landmarks_captures = []
        right_cam_landmarks_captures = []
        history_size = 10
        history_counter = 0
        while self.stereo_cameras.is_started() and history_counter < history_size:
            sleep(0.005)
            left_cam_points_3d, right_cam_points_3d = mocap_hands_core.detects_raw_points_3d_stereo(
                self.stereo_cameras.get_left_camera().get_shared_frame(),
                self.stereo_cameras.get_right_camera().get_shared_frame(),
            )
            if left_cam_points_3d is not None and right_cam_points_3d is not None:
                left_cam_landmarks_captures.append(left_cam_points_3d)
                right_cam_landmarks_captures.append(right_cam_points_3d)
                history_counter += 1
        mocap_hands_core.initialize_trackers_2d(left_cam_landmarks_captures, right_cam_landmarks_captures)
        history_counter = 0
        triangulated_points_3d_captures = []
        while self.stereo_cameras.is_started() and history_counter < history_size:
            left_cam_points_3d, right_cam_points_3d = mocap_hands_core.detects_raw_points_3d_stereo(
                self.stereo_cameras.get_left_camera().get_shared_frame(),
                self.stereo_cameras.get_right_camera().get_shared_frame(),
            )
            if left_cam_points_3d is not None and right_cam_points_3d is not None:
                height, width, _ = self.stereo_cameras.get_left_camera().get_shared_frame().shape
                left_cam_points_3d, right_cam_points_3d = mocap_hands_core.apply_filtration_trackers_2d(left_cam_points_3d, right_cam_points_3d)
                left_cam_points_3d, right_cam_points_3d = mocap_hands_core.convert_for_triangulation(left_cam_points_3d, right_cam_points_3d, Point2D(width, height))
                positions = mocap_hands_core.triangulate_raw_points(
                    left_cam_points_3d,
                    right_cam_points_3d,
                    self.stereo_cameras.get_left_camera().get_intrinsics_matrix(),
                    self.stereo_cameras.get_right_camera().get_intrinsics_matrix(),
                    self.calibration_stereo_data,
                )
                if positions is not None:
                    triangulated_points_3d_captures.append(positions)
                    history_counter += 1
        mocap_hands_core.initialize_trackers_3d(triangulated_points_3d_captures)
        print("Is mocap ready ? " + str(mocap_hands_core.are_2d_trackers_initialized()))
        print("DONE")

    def on_update_image_left_event(self, frame, delta_time):
        left_hand_tracker_2d = self.mocap_hands_core.get_left_camera_hand_tracker_2d()
        if self.debug_2d_landmarks_checkbox.is_active():
            points_3d = left_hand_tracker_2d.detects_raw_points_3d(frame)
            if points_3d is not None:
                height, width, _ = frame.shape
                if left_hand_tracker_2d.is_initialized() and self.debug_2d_kalman_checkbox.is_active():
                    points_3d = left_hand_tracker_2d.apply_filtration(points_3d)
                self.mocap_hands_core.draw_2d_debug(frame, points_3d, Point2D(width, height))
            elif points_3d is None:
                height, width, _ = frame.shape
                if left_hand_tracker_2d.is_initialized() and self.debug_2d_kalman_checkbox.is_active():
                    points_3d = left_hand_tracker_2d.apply_prediction()
                    self.mocap_hands_core.draw_2d_debug(frame, points_3d, Point2D(width, height))

    def on_update_image_right_event(self, frame, delta_time):
        right_hand_tracker_2d = self.mocap_hands_core.get_right_camera_hand_tracker_2d()
        if self.debug_2d_landmarks_checkbox.is_active():
            points_3d = right_hand_tracker_2d.detects_raw_points_3d(frame)
            if points_3d is not None:
                height, width, _ = frame.shape
                if right_hand_tracker_2d.is_initialized() and self.debug_2d_kalman_checkbox.is_active():
                    points_3d = right_hand_tracker_2d.apply_filtration(points_3d)
                self.mocap_hands_core.draw_2d_debug(frame, points_3d, Point2D(width, height))
            elif points_3d is None:
                height, width, _ = frame.shape
                if right_hand_tracker_2d.is_initialized() and self.debug_2d_kalman_checkbox.is_active():
                    points_3d = right_hand_tracker_2d.apply_prediction()
                    self.mocap_hands_core.draw_2d_debug(frame, points_3d, Point2D(width, height))

    def release(self):
        self.stereo_previews.release()