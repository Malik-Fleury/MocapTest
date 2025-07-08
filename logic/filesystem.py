import os
import cv2
import numpy as np

from logic.camera import Camera


class FileSystem:
    def __init__(self, root_path: str) -> None:
        self.root_path = root_path

    def create_root_folder(self) -> None:
        if not os.path.exists(self.root_path):
            os.makedirs(self.root_path)

    def get_root_path(self) -> str:
        return self.root_path

    def get_file_path(self, file_path: str) -> str:
        return self.root_path + file_path

    def get_all_files_paths(self, subfolder: str, extension: str) -> list:
        path = self.get_file_path(subfolder)
        return [os.path.join(path, f) for f in os.listdir(path) if
         f.endswith(extension)]


class ImagesFileSystem(FileSystem):
    def __init__(self, root_path: str) -> None:
        super().__init__(root_path)

    def save_image(self, image_path: str, frame: cv2.Mat | np.ndarray) -> None:
        self.create_root_folder()
        file_path = self.get_file_path(image_path)
        cv2.imwrite(file_path, frame)

    def load_image(self, image_path: str) -> np.ndarray:
        return cv2.imread(self.get_file_path(image_path))

    def get_all_images_paths(self, images_path: str) -> list:
        return super().get_all_files_paths(images_path, '.jpg')


class ConfigsFileSystem(FileSystem):
    def __init__(self, root_path: str) -> None:
        super().__init__(root_path)

    def get_camera_calibration_config_path(self, camera: Camera) -> str:
        return self.root_path + '/' + camera.get_camera_name() + '/calibration.xml'

    def get_stereo_cameras_calibration_config_path(self) -> str:
        return self.root_path + '/stereo/calibration_config.xml'

    def save_camera_calibration_config(self, camera: Camera):
        file_path = self.get_camera_calibration_config_path(camera)
        file_storage = cv2.FileStorage(file_path, cv2.FILE_STORAGE_WRITE)
        file_storage.write("K", camera.get_intrinsics_matrix())
        file_storage.write("D", camera.get_distortion_coefficients())
        file_storage.release()

    def load_camera_calibration_config(self, camera: Camera) -> None:
        file_path = self.get_camera_calibration_config_path(camera)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file doesn't exist in {file_path}")
        file_storage = cv2.FileStorage(file_path, cv2.FILE_STORAGE_READ)
        camera.set_intrinsics_matrix(file_storage.getNode("K").mat())
        camera.set_distortion_coefficients(file_storage.getNode("D").mat())
        file_storage.release()
        camera.set_calibrated(True)

    def save_stereo_cameras_configs(self, camera: Camera):
        pass

    def is_calibration_config_available(self, camera: Camera) -> bool:
        file_path = self.get_camera_calibration_config_path(camera)
        return os.path.exists(file_path)