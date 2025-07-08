import cv2
import numpy as np

from data.calibration_stereo_data import CalibrationStereoData
from data.math.point_3d import Point3D
from logic.mocap.mocap_multi_kalman_filters import MocapMultiFilters


class MocapHandsTracker3D:
    def __init__(self):
        self.multi_filters = MocapMultiFilters(1000, 0.01)
        self.landmarks_number = 21

    def initialize(self, positions_capture):
        self.multi_filters.initialize_filters(positions_capture, self.landmarks_number)

    def is_initialized(self) -> bool:
        return self.multi_filters.are_filters_ready()

    def triangulate_raw_points(self,
                    left_landmarks,
                    right_landmarks,
                    left_intrinsics_matrix,
                    right_intrinsics_matrix,
                    calibration_stereo_data: CalibrationStereoData,
                    ):
        # RT matrix for C1 is identity.
        R = calibration_stereo_data.get_rotation_matrix()
        T = calibration_stereo_data.get_translation_matrix()
        RT1 = np.concatenate([np.eye(3), np.array([[0], [0], [0]])], axis=-1)
        P1 = left_intrinsics_matrix @ RT1  # projection matrix for C1
        # RT matrix for C2 is the R and T obtained from stereo calibration.
        RT2 = np.concatenate([R, T], axis=-1)
        P2 = right_intrinsics_matrix @ RT2  # projection matrix for C2
        # POINTS 4D, 3D
        points4D = cv2.triangulatePoints(P1, P2, left_landmarks.T, right_landmarks.T)
        points3D = points4D[:3, :] / points4D[3, :]  # Convertir en coordonnées 3D
        return points3D.T

    def apply_filtration(self, points_3d: list[Point3D]) -> list[Point3D]:
        filtrated_points = self.multi_filters.correct_and_predict(points_3d)
        return filtrated_points

    def apply_prediction(self) -> list[Point3D]:
        return self.multi_filters.predict()