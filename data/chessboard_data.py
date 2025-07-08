
class ChessboardData:
    def __init__(self, width: int, height: int, square_length: float):
        self.width = width
        self.height = height
        self.square_length = square_length

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def get_size(self) -> tuple:
        return self.width, self.height

    def get_square_length(self) -> float:
        return self.square_length