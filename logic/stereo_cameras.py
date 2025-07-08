import cv2

from data.calibration_data import CalibrationData
from data.calibration_stereo_data import CalibrationStereoData
from logic.camera import Camera
from data.chessboard_data import ChessboardData
from logic.filesystem import ImagesFileSystem

STEREO_LEFT_CAMERA_INDEX = 0
STEREO_RIGHT_CAMERA_INDEX = 1

class StereoCameras:
    def __init__(self, left_camera: Camera, right_camera: Camera):
        self.left_camera =  left_camera
        self.right_camera = right_camera

    def start_all_cameras(self):
        self.left_camera.start()
        self.right_camera.start()

    def stop_all_cameras(self):
        self.left_camera.stop()
        self.right_camera.stop()

    def get_left_camera(self) -> Camera:
        return self.left_camera

    def get_right_camera(self) -> Camera:
        return self.right_camera

    def get_cameras_as_list(self) -> list[Camera]:
        return [self.left_camera, self.right_camera]

    def is_started(self) -> bool:
        return self.left_camera.is_started() and self.right_camera.is_started()

    def get_frames(self) -> list:
        return [self.left_camera.get_frame(), self.right_camera.get_frame()]

    def calibrate_all_cameras_individually(self, image_file_system: ImagesFileSystem, chessboard_data: ChessboardData) -> list:
        calibrations_data_list = []
        for camera in self.get_cameras_as_list():
            calibration_data = self.calibrate_one_camera(camera, image_file_system, chessboard_data)
            calibrations_data_list.append(calibration_data)
        return calibrations_data_list

    def calibrate_one_camera(self, camera: Camera, image_file_system: ImagesFileSystem, chessboard_data: ChessboardData) -> CalibrationData:
        images_paths_list = image_file_system.get_all_images_paths('/' + camera.get_camera_name() + '/')
        return camera.calibrate_new(images_paths_list, chessboard_data)

    def calibrate_stereo_cameras(self, calibration_data_list: list) -> CalibrationStereoData:
        cameras_list = self.get_cameras_as_list()
        retval, K1, D1, K2, D2, R, T, E, F = cv2.stereoCalibrate(
            calibration_data_list[0].get_objects_points(),
            calibration_data_list[0].get_image_points(),
            calibration_data_list[1].get_image_points(),
            cameras_list[0].get_intrinsics_matrix(),
            cameras_list[0].get_distortion_coefficients(),
            cameras_list[1].get_intrinsics_matrix(),
            cameras_list[1].get_distortion_coefficients(),
            (9, 6),
            flags=cv2.CALIB_FIX_INTRINSIC
        )
        calibration_stereo_data = CalibrationStereoData(R, T)
        return calibration_stereo_data