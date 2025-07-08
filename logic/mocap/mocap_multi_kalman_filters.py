from data.filter_data import FilterData
from data.math.point_3d import Point3D
from logic.mocap.mocap_kalman_filter import MocapKalmanFilter


class MocapMultiFilters(object):
    def __init__(self, measure_corrector_factor: float, process_corrector_factor: float):
        self.filters = []
        self.measure_corrector_factor = measure_corrector_factor
        self.process_corrector_factor = process_corrector_factor

    def are_filters_ready(self) -> bool:
        return len(self.filters) > 0

    def initialize_filters(self, positions_captures: list, landmarks_number: int):
        filter_data_list = []
        history_size = len(positions_captures)
        # Create filters data
        for index in range(0, landmarks_number):
            filter_data_list.append(FilterData(history_size))
        # Add points from captures to filters
        for positions_capture in positions_captures:
            for index in range(0, landmarks_number):
                filter_data_list[index].add_point_to_history(positions_capture[index])
        # Create filters
        for filter_data in filter_data_list:
            filter_data.compute_measure_noise()
            self.filters.append(MocapKalmanFilter(filter_data, self.measure_corrector_factor, self.process_corrector_factor))

    def update_measure_factor(self, measure_factor: float):
        for current_filter in self.filters:
            current_filter.update_measure_factor(measure_factor)

    def update_process_factor(self, process_factor: float):
        for current_filter in self.filters:
            current_filter.update_process_factor(process_factor)

    def correct_and_predict(self, points_3d: list[Point3D]) -> list[Point3D]:
        corrected_positions = []
        for index in range(0, len(points_3d)):
            x,y,z = self.filters[index].correct_and_predict(points_3d[index])
            corrected_positions.append(Point3D(x[0],y[0],z[0]))
        return corrected_positions

    def predict(self) -> list[Point3D]:
        predicted_positions = []
        for index in range(0, len(self.filters)):
            x,y,z = self.filters[index].predict()
            predicted_positions.append(Point3D(x,y,z))
        return predicted_positions