import numpy as np


class Point2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def get_x(self) -> float:
        return self.x

    def get_y(self) -> float:
        return self.y

    def to_list(self) -> list[float]:
        return [self.x, self.y]

    def to_np_array(self) -> np.array:
        return np.array(self.to_list())

    def to_tuple(self) -> tuple[float, float]:
        return self.x, self.y