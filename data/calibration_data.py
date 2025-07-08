
class CalibrationData:
    def __init__(self):
        self.image_points = []
        self.objects_points = []

    def get_image_points(self):
        return self.image_points

    def get_objects_points(self):
        return self.objects_points