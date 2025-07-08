import cv2
import numpy as np

from data.filter_data import FilterData
from data.math.point_3d import Point3D


class MocapKalmanFilter:
    def __init__(self, filter_data: FilterData, measure_corrector_factor: float, process_corrector_factor: float):
        self.filter_data = filter_data
        self.kalman = self.create_kalman_filter(
            measure_corrector_factor,
            process_corrector_factor
        )

    def create_kalman_filter(self, measure_corrector_factor: float, process_corrector_factor: float):
        kalman = cv2.KalmanFilter(6, 3)  # 6 états (x, y, z et vitesses) et 3 observations (x, y, z)
        # Définir la matrice de transition d'état (F)
        kalman.transitionMatrix = np.array([
            [1, 0, 0, 1, 0, 0],  # x' = x + vx
            [0, 1, 0, 0, 1, 0],  # y' = y + vy
            [0, 0, 1, 0, 0, 1],  # z' = z + vz
            [0, 0, 0, 1, 0, 0],  # vx' = vx
            [0, 0, 0, 0, 1, 0],  # vy' = vy
            [0, 0, 0, 0, 0, 1],  # vz' = vz
        ], dtype=np.float32)
        # Définir la matrice d'observation (H)
        kalman.measurementMatrix = np.array([
            [1, 0, 0, 0, 0, 0],  # Observation de x
            [0, 1, 0, 0, 0, 0],  # Observation de y
            [0, 0, 1, 0, 0, 0],  # Observation de z
        ], dtype=np.float32)
        pow_standard_deviation = [p for p in self.filter_data.get_standard_deviation()]
        # Matrices de covariance pour le bruit (Q et R)
        kalman.measurementNoiseCov = np.diag(pow_standard_deviation).astype(np.float32)
        kalman.processNoiseCov = np.eye(6, dtype=np.float32) * process_corrector_factor  # Bruit du processus
        kalman.errorCovPost = np.eye(6, dtype=np.float32)
        # État initial
        kalman.statePost = np.zeros(6, dtype=np.float32)
        return kalman

    def update_measure_factor(self, measure_factor: float):
        pow_standard_deviation = [p ** 2 for p in self.filter_data.get_standard_deviation()]
        self.kalman.measurementNoiseCov = np.diag(pow_standard_deviation).astype(np.float32) * measure_factor

    def update_process_factor(self, process_factor: float):
        self.kalman.processNoiseCov = np.eye(6, dtype=np.float32) * process_factor

    def predict(self):
        kalman = self.kalman
        prediction = kalman.predict()
        return [prediction[0], prediction[1], prediction[2]]

    def correct_and_predict(self, point_3d: Point3D):
        kalman = self.kalman
        measure = np.array([[np.float32(point_3d.get_x())],
                            [np.float32(point_3d.get_y())],
                            [np.float32(point_3d.get_z())]])
        kalman.correct(measure)
        prediction = self.predict()
        return np.array(prediction)
