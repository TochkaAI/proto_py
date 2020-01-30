import socket

from strongTcpClient.messagePool import MessagePool


class Connection:
    def __init__(self, socket_=None):
        self.message_pool = MessagePool()
        self.request_pool = MessagePool()

        if socket_ is None:
            socket_ = socket.socket()

        self.socket = socket_

    def setSocket(self, socket_):
        self.socket = socket_

    def getpeername(self):
        return self.socket.getpeername()

    def send(self, bdata):
        return self.socket.send(bdata)

    def connect(self, *args, **kwargs):
        return self.socket.connect(*args, **kwargs)

    def close(self):
        return self.socket.close()

    def msend(self, bdata):
        bdata_len = (len(bdata)).to_bytes(4, 'big')
        self.socket.send(bdata_len + bdata)

    def recv(self, buffsize, timeout=None):
        self.socket.settimeout(timeout)
        try:
            answer = self.socket.recv(buffsize)
            return answer
        except socket.timeout:
            raise TimeoutError('Удалённый сервер не ответил на приветствие в установленное время')
        finally:
            self.socket.settimeout(None)

    def mrecv(self):
        banswer_size = self.socket.recv(4)
        answer_size = int.from_bytes(banswer_size, 'big')
        ball_answer = self.socket.recv(answer_size)
        return ball_answer.decode()