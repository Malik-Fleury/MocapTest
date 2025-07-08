import cv2
import numpy as np
import mediapipe as mp

from data.calibration_stereo_data import CalibrationStereoData
from logic.camera import Camera
from logic.mocap.mocap_internal_results import MocapInternalResults


class MocapCore:
    def __init__(self):
        mp_hands = mp.solutions.hands
        self.left_hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
        self.right_hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
        self.results1 = None
        self.results2 = None
        self.point1_filtered = None
        self.point2_filtered = None
        self.mocap_internal_results = MocapInternalResults()
        self.hand_landmarks_number = 21

    def get_hand_landmarks_number(self) -> int:
        return self.hand_landmarks_number

    def get_frames(self, left_camera: Camera, right_camera: Camera):
        left_frame = left_camera.get_shared_frame()
        right_frame = right_camera.get_shared_frame()
        mtx1 = left_camera.get_intrinsics_matrix()
        mtx2 = right_camera.get_intrinsics_matrix()
        left_frame = cv2.undistort(left_frame, mtx1, left_camera.get_distortion_coefficients(), None, mtx1)
        right_frame = cv2.undistort(right_frame, mtx2, right_camera.get_distortion_coefficients(), None, mtx2)
        # left_frame = cv2.bilateralFilter(left_frame, d=15, sigmaColor=50, sigmaSpace=75)
        # right_frame = cv2.bilateralFilter(right_frame, d=15, sigmaColor=50, sigmaSpace=75)
        return left_frame, right_frame

    def detects_landmarks(self, left_frame, right_frame, mode_interlace = True):
        mocap_internal_results = self.mocap_internal_results
        if mode_interlace:
            if mocap_internal_results.get_results_left_frame() is None or mocap_internal_results.is_pair():
                rgb_left_frame = cv2.cvtColor(left_frame, cv2.COLOR_BGR2RGB)
                left_results = self.left_hands.process(rgb_left_frame)
                mocap_internal_results.set_results_left_frame(left_results)
            if mocap_internal_results.get_results_right_frame() is None or mocap_internal_results.is_pair():
                rgb_right_frame = cv2.cvtColor(right_frame, cv2.COLOR_BGR2RGB)
                right_results = self.right_hands.process(rgb_right_frame)
                mocap_internal_results.set_results_right_frame(right_results)
        else:
            rgb_left_frame = cv2.cvtColor(left_frame, cv2.COLOR_BGR2RGB)
            rgb_right_frame = cv2.cvtColor(right_frame, cv2.COLOR_BGR2RGB)
            left_results = self.left_hands.process(rgb_left_frame)
            right_results = self.right_hands.process(rgb_right_frame)
            mocap_internal_results.set_results_left_frame(left_results)
            mocap_internal_results.set_results_right_frame(right_results)
        return mocap_internal_results.get_results_left_frame(), mocap_internal_results.get_results_right_frame()

    def converts(self, points, width: int, height: int):
        converted_points = []
        for point in points:
            x, y = int(point.x * width), int(point.y * height)
            converted_points.append([x, y])
        return np.array(converted_points, dtype=np.float32)

    def triangulate_from_points_2d(self, rotation_matrix, translation_matrix, left_camera: Camera, right_camera: Camera, left_points, right_points):
        # RT matrix for C1 is identity.
        RT1 = np.concatenate([np.eye(3), np.array([[0], [0], [0]])], axis=-1)
        P1 = left_camera.get_intrinsics_matrix() @ RT1  # projection matrix for C1
        # RT matrix for C2 is the R and T obtained from stereo calibration.
        RT2 = np.concatenate([rotation_matrix, translation_matrix], axis=-1)
        P2 = right_camera.get_intrinsics_matrix() @ RT2  # projection matrix for C2
        points_4d = cv2.triangulatePoints(P1, P2, left_points.T, right_points.T)
        points_3d = points_4d[:3, :] / points_4d[3, :]  # Convertir en coordonnées 3D
        return points_3d.T

    def full_process(self, left_camera: Camera, right_camera: Camera, calibration_stereo_data: CalibrationStereoData, mode_interlace = True):
        points_3d = None
        left_frame, right_frame = self.get_frames(left_camera, right_camera)
        results_left_frame, results_right_frame = self.detects_landmarks(left_frame, right_frame, mode_interlace)
        if results_left_frame is not None and results_right_frame is not None:
            if results_left_frame.multi_hand_landmarks is not None and results_right_frame.multi_hand_landmarks is not None:
                height, width = left_frame.shape[:2]
                left_points_3d = self.converts(results_left_frame.multi_hand_landmarks[0].landmark, width, height)
                height, width = left_frame.shape[:2]
                right_points_3d = self.converts(results_right_frame.multi_hand_landmarks[0].landmark, width, height)
                points_3d = self.triangulate_from_points_2d(
                    calibration_stereo_data.get_rotation_matrix(), calibration_stereo_data.get_translation_matrix(),
                    left_camera, right_camera,
                    left_points_3d, right_points_3d)
        if mode_interlace:
            self.mocap_internal_results.increment_counter()
        return points_3d

    # OLD; Dépréciée
    def triangulate(self, R, T, left_camera: Camera, right_camera: Camera, v: int, mode_interlace = True):
        frame1 = left_camera.get_shared_frame()
        frame2 = right_camera.get_shared_frame()

        h1, w1 = frame1.shape[:2]
        h2, w2 = frame2.shape[:2]

        mtx1 = left_camera.get_intrinsics_matrix()
        mtx2 = right_camera.get_intrinsics_matrix()

        frame1 = cv2.undistort(frame1, mtx1, left_camera.get_distortion_coefficients(), None, mtx1)
        frame2 = cv2.undistort(frame2, mtx2, right_camera.get_distortion_coefficients(), None, mtx2)
        #frame1 = cv2.GaussianBlur(frame1, (5, 5), 0)
        #frame2 = cv2.GaussianBlur(frame2, (5, 5), 0)

        # A VOIR SI NECESSAIRE
        frame1 = cv2.bilateralFilter(frame1, d=15, sigmaColor=50, sigmaSpace=75)
        frame2 = cv2.bilateralFilter(frame2, d=15, sigmaColor=50, sigmaSpace=75)

        results1 = self.results1
        results2 = self.results2

        if mode_interlace:
            if results1 is None or v % 2 == 0:
                rgb_frame_1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                results1 = self.left_hands.process(rgb_frame_1)
                self.results1 = results1
                #print("process results1: " + str(v))
            if results2 is None or v % 2 == 1:
                rgb_frame_2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
                results2 = self.right_hands.process(rgb_frame_2)
                self.results2 = results2
                #print("process results2: " + str(v))
        else:
            rgb_frame_1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
            rgb_frame_2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
            results1 = self.left_hands.process(rgb_frame_1)
            results2 = self.right_hands.process(rgb_frame_2)
            self.results1 = results1
            self.results2 = results2

        # A BOUGER DANS UNE FONCTION DE CONVERSION DE TYPE DE TABLEAU
        if results1 is not None and results2 is not None and results1.multi_hand_landmarks is not None and results2.multi_hand_landmarks is not None:
            points1 = []
            points2 = []
            for lm1, lm2 in zip(results1.multi_hand_landmarks[0].landmark, results2.multi_hand_landmarks[0].landmark):
                # Convertir en pixels
                x1, y1 = int(lm1.x * w1), int(lm1.y * h1)
                x2, y2 = int(lm2.x * w2), int(lm2.y * h2)
                # Ajouter les points
                points1.append([x1, y1])
                points2.append([x2, y2])

            points1 = np.array(points1, dtype=np.float32)
            points2 = np.array(points2, dtype=np.float32)

            # FILTRE EXPO.
            alpha = 0.5
            if self.point1_filtered is None:
                self.point1_filtered = points1
            else:
                self.point1_filtered = points1 * alpha + (1 - alpha) * self.point1_filtered

            if self.point2_filtered is None:
                self.point2_filtered = points2
            else:
                self.point2_filtered = points2 * alpha + (1 - alpha) * self.point2_filtered
            # -----------------------------

            # A BOUGER DANS UNE FONCTION SPECIFIQUE AU CALCUL 3D
            # RT matrix for C1 is identity.
            RT1 = np.concatenate([np.eye(3),  np.array([[0], [0], [0]])], axis=-1)
            P1 = mtx1 @ RT1  # projection matrix for C1

            # RT matrix for C2 is the R and T obtained from stereo calibration.
            RT2 = np.concatenate([R, T], axis=-1)
            P2 = mtx2 @ RT2  # projection matrix for C2

            points4D = cv2.triangulatePoints(P1, P2, points1.T, points2.T)
            points3D = points4D[:3, :] / points4D[3, :]  # Convertir en coordonnées 3D
            return points3D.T
        else:
            return None
