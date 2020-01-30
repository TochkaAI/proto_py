import socket
import uuid
from threading import Thread
import json

from strongTcpClient import baseCommands
from strongTcpClient.message import Message


class StrongClient:
    def __init__(self, ip='127.0.0.1', port=48062):
        self.ip = ip
        self.port = port

        self.isRunning = False

        self.sock = socket.socket()
        self.thread = Thread(target=self.main_listener)

    def send(self, bdata):
        self.sock.send(bdata)

    def msend(self, bdata):
        bdata_len = (len(bdata)).to_bytes(4, 'big')
        self.sock.send(bdata_len + bdata)

    def recv(self, buffsize, timeout=None):
        self.sock.settimeout(timeout)
        try:
            answer = self.sock.recv(buffsize)
            return answer
        except socket.timeout as timeex:
            raise TimeoutError('Удалённый сервер не ответил на приветствие в установленное время')
        finally:
            self.sock.settimeout(None)

    def mrecv(self):
        banswer_size = self.recv(4)
        answer_size = int.from_bytes(banswer_size, 'big')
        ball_answer = self.recv(answer_size)
        return ball_answer.decode()

    def send_message(self, message):
        self.msend(message.getBytes())

    def send_hello(self):
        bdata = uuid.UUID(baseCommands.JSON_PROTOCOL_FORMAT).bytes
        self.send(bdata)
        answer = self.recv(16, timeout=3)
        if answer != bdata:
            raise TypeError('Удалённый сервер не согласовал тип протокола')

    def protocol_compatible(self):
        msg = Message.command(baseCommands.PROTOCOL_COMPATIBLE)
        self.send_message(msg)

        answer = self.mrecv()
        msg = Message.fromString(answer)

    def main_listener(self):
        while self.isRunning:
            answer = self.mrecv()
            if answer is not None:
                print(f'Msg JSON receeved: {answer}')
                msg = Message.fromString(answer)
                print(f'Msg received: {msg}')

        print('end of listening')

    def start(self):
        ''' Порядок установки соединения '''
        try:
            self.sock.connect((self.ip, self.port))
        except ConnectionRefusedError as ex:
            print('Не удалось, установить соединение, удалённый сервер не доступен')
            return
        ''' После установки TCP соединения клиент отправляет на сокет сервера 16 байт (обычный uuid). 
            Это сигнатура протокола. Строковое представление сигнатуры для json формата: "fea6b958-dafb-4f5c-b620-fe0aafbd47e2". 
            Если сервер присылает назад этот же uuid, то все ОК - можно работать'''
        self.send_hello()
        ''' После того как сигнатуры протокола проверены клиент и сервер отправляют друг другу первое сообщение - 
            ProtocolCompatible.'''
        self.protocol_compatible()

        self.isRunning = True
        self.thread.start()

    def finish(self):
        self.isRunning = False
        content = dict(
            code=1,
            description='Bye bye!'
        )
        msg = Message.command(baseCommands.CLOSE_CONNECTION)
        msg.setContent(content)
        self.send_message(msg)
