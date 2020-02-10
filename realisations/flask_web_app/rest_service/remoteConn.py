from . import userCommands, userCommandsImpl
from packages.strongTcpClient.tcpSocket import TcpSocket


class TcpConnectionWorker:
    def __init__(self):
        self.tcp_connection = self.create_connection()

    @staticmethod
    def connection_is_dead(connection):
        print(f'connection {connection.getpeername()} was closed')

    @staticmethod
    def create_connection():
        ip_to_connect = '127.0.0.1'
        port_to_connect = 48062
        tcp_worker = TcpSocket(ip_to_connect, port_to_connect, userCommands, userCommandsImpl)
        return tcp_worker.connect(TcpConnectionWorker.connection_is_dead)

    def reconect(self):
        if not self.tcp_connection or not self.tcp_connection.is_connected():
            self.tcp_connection = TcpConnectionWorker.create_connection()
        return self.tcp_connection

    def get_connection(self):
        return self.tcp_connection


CONNECTION = TcpConnectionWorker()
