
class RollHistoryData:
    def __init__(self, size = 10):
        self.size = size
        self.roll_history = []

    def add_to_history(self, data):
        self.roll_history.append(data)
        if not self.size >= len(self.roll_history):
            self.roll_history.pop(0)

    def get_roll_history(self):
        return self.roll_history

    def get_size(self):
        return self.size

    def is_full(self) -> bool:
        return len(self.roll_history) >= self.size