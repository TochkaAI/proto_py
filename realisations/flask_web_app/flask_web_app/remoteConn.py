import userCommands, userCommandsImpl
from packages.strongTcpClient.tcpSocket import TcpSocket


def create_connection_singleton():
    ip_to_connect = '127.0.0.1'
    port_to_connect = 48062
    tcp_worker = TcpSocket(ip_to_connect, port_to_connect, userCommands, userCommandsImpl)
    return tcp_worker.connect()


CONNECTION = create_connection_singleton()
