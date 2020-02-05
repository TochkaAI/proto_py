import socket
from threading import Thread

from strongTcpClient.worker import TcpWorker
from strongTcpClient.connection import Connection
from strongTcpClient.logger import write_info


class TcpServer(TcpWorker):
    '''сущность которая выступает в роли слушателья
    к ней можно подключится образовав тем самым конекцию, для дальнейшего обмена сообщениями'''
    def __init__(self, ip, port, client_commands, client_command_impl):
        super().__init__(ip, port, client_commands, client_command_impl)

        self.serv_socket = socket.socket()

    def connect_listener(self, new_client_handler):
        while True:
            sock, adr = self.serv_socket.accept()
            # TODO: чёт не очевидно оказалось в питоне отслеживать разъединение с сокетом. оставлю на след неделю,
            # TODO: оответственно дисконект хэндлер тоже на это завязан, по этому он пока тоже без реализации
            conn = Connection(self, sock)
            write_info(f'{conn.getpeername()} - was connected')
            self.start(conn)

            if new_client_handler:
                new_client_handler(conn)

    def run(self, new_connection_handler=None, disconect_connection_handler=None):
        self.serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv_socket.bind((self.ip, self.port))
        self.serv_socket.listen(10)

        thread = Thread(target=self.connect_listener, args=(new_connection_handler,))
        thread.daemon = True
        thread.start()

        self._set_disconnection_handler(disconect_connection_handler)

    def stop(self):
        self.finish_all(0, 'Good bye!')
        self.serv_socket.shutdown(socket.SHUT_RDWR)
        self.serv_socket.close()
