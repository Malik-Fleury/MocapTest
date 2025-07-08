import socket

class UdpServer:
    def __init__(self, target_ip: str, port: int):
        self.target_ip = target_ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data: bytes):
        self.socket.sendto(data, (self.target_ip, self.port))