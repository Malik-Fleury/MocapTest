import cv2
import numpy as np

from data.calibration_stereo_data import CalibrationStereoData
from data.math.point_2d import Point2D
from data.math.point_3d import Point3D
from logic.mocap.mocap_hands_tracker_2d import MocapHandsTracker2D
from logic.mocap.mocap_hands_tracker_3d import MocapHandsTracker3D


class MocapHandsCore:
    def __init__(self):
        self.mocap_left_cam_hands_tracker_2d = MocapHandsTracker2D()
        self.mocap_right_cam_hands_tracker_2d = MocapHandsTracker2D()
        self.mocap_hands_tracker_3d = MocapHandsTracker3D()

    def initialize_trackers_2d(self, left_positions_captures: list[Point3D], right_positions_captures: list[Point3D]):
        self.mocap_left_cam_hands_tracker_2d.initialize(left_positions_captures)
        self.mocap_right_cam_hands_tracker_2d.initialize(right_positions_captures)

    def initialize_trackers_3d(self, positions_captures: list[Point3D]):
        self.mocap_hands_tracker_3d.initialize(positions_captures)

    def are_2d_trackers_initialized(self) -> bool:
        return self.mocap_left_cam_hands_tracker_2d.is_initialized() and self.mocap_right_cam_hands_tracker_2d.is_initialized()

    def is_3d_tracker_initialized(self) -> bool:
        return self.mocap_hands_tracker_3d.is_initialized()

    def detects_raw_points_3d_stereo(self, left_frame, right_frame):
        left_cam_landmarks = self.mocap_left_cam_hands_tracker_2d.detects_raw_points_3d(left_frame)
        right_cam_landmarks = self.mocap_right_cam_hands_tracker_2d.detects_raw_points_3d(right_frame)
        return left_cam_landmarks, right_cam_landmarks

    def draw_2d_debug(self, frame, points_3d: list[Point3D], frame_size: Point2D) -> None:
        for point_3d in points_3d:
            size = (int(point_3d.get_x() * frame_size.get_x()), int(point_3d.get_y() * frame_size.get_y()))
            cv2.circle(frame, size, 5, (0, 255, 0), -1)

    def apply_filtration_trackers_2d(self, left_cam_points_3d: list[Point3D], right_cam_points_3d: list[Point3D]):
        left_cam_filtered_points_3d = self.mocap_left_cam_hands_tracker_2d.apply_filtration(left_cam_points_3d)
        right_cam_filtered_points_3d = self.mocap_right_cam_hands_tracker_2d.apply_filtration(right_cam_points_3d)
        return left_cam_filtered_points_3d, right_cam_filtered_points_3d

    def apply_filtration_tracker_3d(self, raw_positions_3d: list[Point3D]):
        return self.mocap_hands_tracker_3d.apply_filtration(raw_positions_3d)

    def convert_for_triangulation(self, left_cam_points_3d: list[Point3D], right_cam_points_3d: list[Point3D], frame_size: Point2D):
        left_cam_points_3d = np.array([(point_3d.x * frame_size.x, point_3d.y * frame_size.y) for point_3d in left_cam_points_3d])
        right_cam_points_3d = np.array([(point_3d.x * frame_size.x, point_3d.y * frame_size.y) for point_3d in right_cam_points_3d])
        return left_cam_points_3d, right_cam_points_3d

    def triangulate_raw_points(self,
                       left_landmarks,
                       right_landmarks,
                       left_intrinsics_matrix,
                       right_intrinsics_matrix,
                       calibration_stereo_data: CalibrationStereoData,
                    ):
        positions = self.mocap_hands_tracker_3d.triangulate_raw_points(left_landmarks,
                                                                  right_landmarks,
                                                                  left_intrinsics_matrix,
                                                                  right_intrinsics_matrix,
                                                                  calibration_stereo_data)
        return [Point3D(position[0], position[1], position[2]) for position in positions]

    def get_left_camera_hand_tracker_2d(self) -> MocapHandsTracker2D:
        return self.mocap_left_cam_hands_tracker_2d

    def get_right_camera_hand_tracker_2d(self) -> MocapHandsTracker2D:
        return self.mocap_right_cam_hands_tracker_2d

    def get_hands_tracker_3d(self) -> MocapHandsTracker3D:
        return self.mocap_hands_tracker_3d