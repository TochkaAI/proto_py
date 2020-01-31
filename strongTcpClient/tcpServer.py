import socket
from threading import Thread

from strongTcpClient.worker import TcpWorker
from strongTcpClient.connection import Connection
from strongTcpClient.logger import write_info


class TcpServer(TcpWorker):
    def connect_listener(self, serv_sock, new_client_handler):
        while True:
            sock, adr = serv_sock.accept()
            # TODO: чёт не очевидно оказалось в питоне отслеживать разъединение с сокетом. оставлю на след неделю,
            # TODO: оответственно дисконект хэндлер тоже на это завязан, по этому он пока тоже без реализации
            conn = Connection(self, sock)
            write_info(f'{conn.getpeername()} - was connected')
            self.start(conn)

            if new_client_handler:
                new_client_handler(conn)

    def run(self, new_client_handler=None):
        serv_sock = socket.socket()
        serv_sock.bind((self.ip, self.port))
        serv_sock.listen(10)

        thread = Thread(target=self.connect_listener, args=(serv_sock, new_client_handler))
        thread.daemon = True
        thread.start()

    def stop(self):
        self.finish_all(0, 'Good bye!')
