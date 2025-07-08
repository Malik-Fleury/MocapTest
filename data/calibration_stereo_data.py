
class CalibrationStereoData:
    def __init__(self, R, T):
        self.T = T
        self.R = R

    def get_rotation_matrix(self):
        return self.R

    def get_translation_matrix(self):
        return self.T