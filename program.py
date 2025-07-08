from time import sleep

import cv2

from logic.camera import Camera
from data.chessboard_data import ChessboardData
from logic.filesystem import ImagesFileSystem, ConfigsFileSystem
from logic.mocap.mocap_core import MocapCore
from logic.packet_builder import PacketBuilder
from logic.stats import Stats
from logic.stereo_cameras import StereoCameras
from logic.udp_server import UdpServer


class Program:
    def __init__(self):
        self.imagesFileSystem = ImagesFileSystem('./images')
        self.configsFileSystem = ConfigsFileSystem('./configs')
        self.stereo_cameras = StereoCameras(Camera(1, 30, False), Camera(0, 30, False))
        self.chessboard_data = ChessboardData(9, 6, 0.016)
        self.mocap_core = MocapCore()
        self.packet_builder = PacketBuilder()
        self.udp_server = UdpServer('127.0.0.1', 5005)
        self.stats = Stats()

    def take_pictures_for_calibration(self) -> None:
        print('Starting soon...')
        sleep(5)
        print('Starting now !')
        for i in range(0, 20):
            sleep(3)
            print('Picture #', i)
            for camera in self.stereo_cameras.get_cameras_as_list():
                frame = camera.get_frame()
                cv2.imshow('Chessboard Pictures', frame)
                self.imagesFileSystem.save_image(('/' + camera.get_camera_name() + '/picture_' + str(i) + '.jpg'), frame)
        print('Finished !')

    def calibrate_cameras_individually(self) -> None:
        self.stereo_cameras.calibrate_all_cameras_individually(self.imagesFileSystem, self.chessboard_data)
        for camera in self.stereo_cameras.get_cameras_as_list():
            self.configsFileSystem.save_camera_calibration_config(camera)

    def calibrate_stereo_cameras(self) -> None:
        calibration_data_list = self.stereo_cameras.calibrate_all_cameras_individually(self.imagesFileSystem, self.chessboard_data)
        calibration_stereo_data = self.stereo_cameras.calibrate_stereo_cameras(calibration_data_list)

    def execute_full_logic(self) -> None:
        print('Calibration camera')
        calibration_data_list = self.stereo_cameras.calibrate_all_cameras_individually(self.imagesFileSystem, self.chessboard_data)
        print('Calibration stereo')
        calibration_stereo_data = self.stereo_cameras.calibrate_stereo_cameras(calibration_data_list)
        print('Mocap core...')
        left_camera = self.stereo_cameras.get_left_camera()
        right_camera = self.stereo_cameras.get_right_camera()

        v = 0
        while self.stereo_cameras.is_started():
            positions = self.mocap_core.triangulate(
                calibration_stereo_data.get_rotation_matrix(),
                calibration_stereo_data.get_translation_matrix(),
                left_camera,
                right_camera,
                v
            )
            if positions is not None:
                packet = self.packet_builder.build_hand_packet(positions)
                self.udp_server.send(packet)

            self.stats.increment_frame_counter()
            fps = self.stats.compute_fps()
            #print(fps)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
            # cv2.imshow('Mocap', left_camera.get_frame())
            v += 1
        print('Finished')

    def takes_pictures(self):
        sleep(3)
        left_frame = self.stereo_cameras.get_left_camera().get_frame()
        right_frame = self.stereo_cameras.get_right_camera().get_frame()
        self.imagesFileSystem.save_image('/tests/images_test_0.jpg', left_frame)
        self.imagesFileSystem.save_image('/tests/images_test_1.jpg', right_frame)

    def execute(self):
        self.stereo_cameras.start_all_cameras()
        self.execute_full_logic()
        self.stereo_cameras.stop_all_cameras()


if __name__ == '__main__':
    program = Program()
    program.execute()
    # camera = Camera(1)
    # camera.start()
    # while camera.is_started():
    #     frame = camera.get_frame()
    #     cv2.imshow('Show', frame)
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break
    # camera.stop()