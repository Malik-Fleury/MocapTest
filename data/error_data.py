
class ErrorData:
    def __init__(self, mean, standard_deviation, covariance_matrix):
        self.mean = mean
        self.standard_deviation = standard_deviation
        self.covariance_matrix = covariance_matrix

    def get_mean(self):
        return self.mean

    def get_standard_deviation(self):
        return self.standard_deviation

    def get_covariance_matrix(self):
        return self.covariance_matrix