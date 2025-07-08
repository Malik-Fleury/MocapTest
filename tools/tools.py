import numpy as np


class Tools:
    @staticmethod
    def converts_2d_points_to_3d_points(points_2d):
        points_3d = []
        for point_2d in points_2d:
            point_3d = Tools.converts_2d_point_to_3d_point(point_2d)
            points_3d.append(point_3d)
        return np.array(points_3d)

    @staticmethod
    def converts_2d_point_to_3d_point(point_2d):
        return [point_2d[0], point_2d[1], 0]