import numpy as np

from data.math.point_3d import Point3D
from logic.common.roll_history_data import RollHistoryData

class FilterData:
    def __init__(self, history_size = 10):
        self.roll_history_data = RollHistoryData(history_size)
        self.standard_deviation = None

    def add_point_to_history(self, point: Point3D):
        self.roll_history_data.add_to_history(point)

    def has_enough_history(self) -> bool:
        return self.roll_history_data.is_full()

    def is_complete(self):
        return self.standard_deviation is not None and self.has_enough_history()

    def compute_measure_noise(self) -> None:
        if self.roll_history_data.is_full():
            points = np.array([point.to_list() for point in self.roll_history_data.get_roll_history()])
            standard_deviation_results = np.std(points, axis=0)
        else:
            raise RuntimeError("Not enough roll history to compute measure noise")
        self.standard_deviation = standard_deviation_results

    def get_standard_deviation(self):
        return self.standard_deviation


if __name__ == "__main__":
    data = FilterData(3)
    data.add_point_to_history(Point3D(0, 0, 0))
    data.add_point_to_history(Point3D(1, 0, 0))
    data.add_point_to_history(Point3D(1.5, 0, 0))
    data.compute_measure_noise()
    print(data.get_standard_deviation())