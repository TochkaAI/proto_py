import socket
from threading import Thread

from .tcpWorker import TcpWorker
from .connection import Connection
from .logger import logger


class TcpServer(TcpWorker):
    """
    Сущность, которая выступает в роли слушателя
    к ней можно подключится образовав тем самым конекцию, для дальнейшего обмена сообщениями
    """
    def __init__(self, ip, port, client_commands, client_command_impl):
        super().__init__(ip, port, client_commands, client_command_impl)

        self.serv_socket = socket.socket()

        self._listener_interrupted = False
        self._listener_thread = None

    def stop_connect_listener(self):
        self._listener_interrupted = True
        if self._listener_thread: self._listener_thread.join()

    def connect_listener(self, new_client_handler, interrupted):
        while not interrupted():
            try:
                sock, adr = self.serv_socket.accept()
            except socket.timeout:
                continue
            connection = Connection(self, sock)
            logger.info(f'{connection.getpeername()} - was connected')
            self.run_connection(connection)

            if new_client_handler:
                new_client_handler(connection)

    def run(self, new_connection_handler=None, disconnect_connection_handler=None):
        self.serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv_socket.bind((self.ip, self.port))
        self.serv_socket.listen(10)
        # Таймаут на socket.accept() 1с.
        self.serv_socket.settimeout(1)

        self._listener_thread = Thread(target=self.connect_listener, args=(new_connection_handler, lambda: self._listener_interrupted))
        self._listener_thread.daemon = True
        self._listener_thread.start()

        self.set_disconnection_handler(disconnect_connection_handler)

    def stop(self):
        self.finish_all(0, 'ef36429c-0661-4264-b982-5af39d3d0bcd', 'Good bye!')
        self.stop_connect_listener()
        self.serv_socket.shutdown(socket.SHUT_RDWR)
        self.serv_socket.close()
