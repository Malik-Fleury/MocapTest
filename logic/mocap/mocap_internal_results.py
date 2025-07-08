
class MocapInternalResults(object):
    def __init__(self):
        self.results_left_frame = None
        self.results_right_frame = None
        self.counter = 0

    def get_results_left_frame(self):
        return self.results_left_frame

    def get_results_right_frame(self):
        return self.results_right_frame

    def set_results_left_frame(self, results_left_frame):
        self.results_left_frame = results_left_frame

    def set_results_right_frame(self, results_right_frame):
        self.results_right_frame = results_right_frame

    def get_counter(self) -> int:
        return self.counter

    def increment_counter(self):
        self.counter += 1

    def is_pair(self) -> bool:
        return self.counter % 2 == 0