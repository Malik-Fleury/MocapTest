from threading import Lock
from threading import Thread

import cv2
import numpy as np
import os

from data.calibration_data import CalibrationData
from data.chessboard_data import ChessboardData
from logic.stats import Stats


class Camera(object):
    def __init__(self, capture_id: int, fps: int, shared_mode = False, distorted = False) -> None:
        self.capture_id = capture_id
        self.lock = Lock()
        self.fps = fps
        self.shared_mode = shared_mode
        self.distorted = distorted
        self.last_frame = None
        self.capture = None
        self.intrinsics_matrix = None
        self.distortion_coefficients = None
        self.translation_matrix = None
        self.rotation_matrix = None
        self.stats = Stats()
        self.calibrated = False

    def start(self) -> None:
        self.capture = cv2.VideoCapture(self.capture_id, cv2.CAP_DSHOW)
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.capture.set(cv2.CAP_PROP_FPS, self.fps)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if not self.is_started():
            raise IOError("Could not open camera")
        if self.shared_mode:
            Thread(target=self.update_frame, daemon=True).start()

    def stop(self) -> None:
        if self.is_started():
            self.capture.release()

    def is_started(self) -> bool:
        return self.capture is not None and self.capture.isOpened()

    def is_frame_available(self) -> bool:
        return self.last_frame is not None

    def is_calibrated(self) -> bool:
        return self.calibrated

    def set_calibrated(self, calibrated = False) -> None:
        self.calibrated = calibrated

    def get_capture_id(self) -> int:
        return self.capture_id

    def update_frame(self) -> None:
        while self.is_started():
            frame = self.get_frame()
            self.stats.increment_frame_counter()
            self.stats.compute_fps()
            with self.lock:
                self.last_frame = frame

    def get_fps_stats(self) -> int:
        return int(self.stats.fps)

    def get_shared_frame(self) -> np.ndarray:
        if not self.shared_mode:
            raise IOError("You can't use this method with shared_mode=FALSE")
        with self.lock:
            last_frame = self.last_frame.copy()
        return last_frame

    def get_frame(self) -> np.ndarray:
        result, frame = self.capture.read()
        if not result:
            raise IOError("Could not read frame")
        if self.distorted and self.is_calibrated():
            frame = cv2.undistort(frame, self.intrinsics_matrix, self.distortion_coefficients, None, self.intrinsics_matrix)
        #frame = cv2.bilateralFilter(frame, d=15, sigmaColor=75, sigmaSpace=75)
        return frame

    def get_fps(self):
        return self.fps

    def is_shared_mode(self) -> bool:
        return self.shared_mode

    def calibrate_new(self, images_list: list, chessboard_data: ChessboardData) -> CalibrationData:
        return self.calibrate(images_list, chessboard_data.get_square_length(), chessboard_data.get_width(), chessboard_data.get_height())

    def calibrate(self, images_list: list, square_size: float, width=9, height=6) -> CalibrationData:
        # Arrays to store object points and image points from all images
        calibration_data = CalibrationData()
        chessboard_size = (width, height)
        # Prepare object points (0,0,0), (1,0,0), (2,0,0), ...
        objp = np.zeros((width * height, 3), np.float32)
        objp[:, :2] = np.mgrid[0:width, 0:height].T.reshape(-1, 2)
        objp *= square_size
        # LOOP
        for image_path in images_list:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Find the chessboard corners
            result, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
            # If found, add object points, image points (after refining them)
            if result:
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1),
                                            criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
                calibration_data.get_objects_points().append(objp)
                calibration_data.get_image_points().append(corners2)
        if len(calibration_data.get_objects_points()) > 0:
            result, intrinsics_matrix, distortion_coefficients, _, _ = cv2.calibrateCamera(calibration_data.get_objects_points(), calibration_data.get_image_points(), gray.shape[::-1], None, None)
            if result:
                self.calibrated = True
                self.intrinsics_matrix = intrinsics_matrix
                self.distortion_coefficients = distortion_coefficients
        return calibration_data

    def get_camera_name(self) -> str:
        return 'cam' + str(self.capture_id)

    def get_calibration_file_path(self) -> str:
        return './configs/' + self.get_camera_name() + '/calibration.xml'

    def save_calibration(self) -> None:
        fs = cv2.FileStorage("calibration.xml", cv2.FILE_STORAGE_WRITE)
        fs.write("K", self.intrinsics_matrix)
        fs.write("D", self.distortion_coefficients)
        fs.release()

    def load_calibration(self) -> None:
        path = self.get_calibration_file_path()
        if not os.path.exists(path):
            raise FileNotFoundError(f"The file doesn't exist in {path}")
        fs = cv2.FileStorage("calibration_data.xml", cv2.FILE_STORAGE_READ)
        self.intrinsics_matrix = fs.getNode("K").mat()
        self.distortion_coefficients = fs.getNode("D").mat()
        self.calibrated = True
        fs.release()

    def is_calibration_config_available(self) -> bool:
        return os.path.exists(self.get_calibration_file_path())

    def get_distortion_coefficients(self) -> np.ndarray:
        return self.distortion_coefficients

    def set_distortion_coefficients(self, distortion_coefficients: np.ndarray) -> None:
        self.distortion_coefficients = distortion_coefficients

    def get_intrinsics_matrix(self) -> np.ndarray:
        return self.intrinsics_matrix

    def set_intrinsics_matrix(self, intrinsics_matrix: np.ndarray) -> None:
        self.intrinsics_matrix = intrinsics_matrix
