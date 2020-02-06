from django.apps import AppConfig

from . import userCommands, userCommandsImpl
from packages.strongTcpClient.tcpSocket import TcpSocket

CONNECTION = None


class TcpClientConfig(AppConfig):
    name = 'singleton_tcp'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)

    @staticmethod
    def create_connection_singleton():
        ip_to_connect = '127.0.0.1'
        port_to_connect = 48062
        tcp_worker = TcpSocket(ip_to_connect, port_to_connect, userCommands, userCommandsImpl)
        return tcp_worker.connect()

    def ready(self):
        global CONNECTION
        CONNECTION = self.create_connection_singleton()

