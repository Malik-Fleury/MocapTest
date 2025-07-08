from typing import Optional

import cv2
import mediapipe as mp
import numpy as np

from data.math.point_3d import Point3D
from logic.mocap.mocap_multi_kalman_filters import MocapMultiFilters


class MocapHandsTracker2D:
    def __init__(self):
        mp_hands = mp.solutions.hands
        self.hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
        self.multi_filters = MocapMultiFilters(1000, 0.00001)
        self.landmarks_number = 21

    def initialize(self, positions_capture: list) -> None:
        self.multi_filters.initialize_filters(positions_capture, self.landmarks_number)

    def is_initialized(self) -> bool:
        return self.multi_filters.are_filters_ready()

    def get_landmarks_number(self) -> int:
        return self.landmarks_number

    def detects_raw_points_3d(self, frame) -> Optional[list[Point3D]]:
        points_3d = None
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detections = self.hands.process(rgb_frame)
        if detections is not None and detections.multi_hand_landmarks is not None:
            raw_landmarks = detections.multi_hand_landmarks[0].landmark
            points_3d = [Point3D(raw_landmark.x, raw_landmark.y, 0) for raw_landmark in raw_landmarks]
        return points_3d

    def apply_filtration(self, points_3d: list[Point3D]) -> list[Point3D]:
        filtrated_points = self.multi_filters.correct_and_predict(points_3d)
        return filtrated_points

    def apply_prediction(self) -> list[Point3D]:
        return self.multi_filters.predict()