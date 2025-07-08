import cv2

from data.chessboard_data import ChessboardData
from logic.stereo_cameras import StereoCameras


class Calibrator:
    def __init__(self, chessboard_data: ChessboardData):
        self.chessboard_data = chessboard_data

    def is_chessboard_on_picture(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result, corners = cv2.findChessboardCorners(gray_frame, self.chessboard_data.get_size(), None)
        average_position = None
        if result:
            average_position = self.compute_average(corners)
        return result, average_position

    def compute_average(self, corners) -> tuple:
        average_x = 0
        average_y = 0
        for corner in corners:
            average_x += corner[0][0]
            average_y += corner[0][1]
        num_corners = len(corners)
        return int(average_x / num_corners), int(average_y / num_corners)

    def capture_stereo(self, stereo_cameras: StereoCameras):
        left_frame = stereo_cameras.get_left_camera().get_frame()
        right_frame = stereo_cameras.get_right_camera().get_frame()
        result1, average_point1 = self.is_chessboard_on_picture(left_frame)
        result2, average_point2 = self.is_chessboard_on_picture(right_frame)
        return result1 and result2, left_frame, right_frame
