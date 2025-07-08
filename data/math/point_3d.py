import numpy as np


class Point3D:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def get_x(self) -> float:
        return self.x

    def get_y(self) -> float:
        return self.y

    def get_z(self) -> float:
        return self.z

    def to_list(self) -> list[float]:
        return [self.x, self.y, self.z]

    def to_np_array(self) -> np.array:
        return np.array(self.to_list())

    def to_tuple(self) -> tuple[float, float, float]:
        return self.x, self.y, self.z