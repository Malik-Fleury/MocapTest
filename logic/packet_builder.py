import struct

from data.math.point_3d import Point3D


class PacketBuilder:
    def __init__(self):
        pass

    def build_hand_packet(self, positions: list[Point3D]) -> bytes:
        num_points = len(positions)
        packet = struct.pack("I", num_points)  # Number of points
        for position in positions:
            packet += struct.pack("fff", position.get_x(), position.get_y(), position.get_z())  # 12 bytes per point (x, y ,z), as float
        return packet