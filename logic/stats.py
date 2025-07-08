import time


class Stats:
    def __init__(self):
        self.frame_counter = 0
        self.start_time = time.time()
        self.fps = 0

    def reset(self):
        self.frame_counter = 0
        self.start_time = time.time()

    def increment_frame_counter(self):
        self.frame_counter += 1

    def compute_fps(self) -> int:
        elapsed_time = time.time() - self.start_time
        if elapsed_time >= 1.0:
            self.fps = self.frame_counter / elapsed_time
            self.reset()
        return int(self.fps)
