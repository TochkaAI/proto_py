import socket
import uuid
from threading import Thread

from strongTcpClient import baseCommands
from strongTcpClient.message import Message
from strongTcpClient.messagePool import MessagePool


class StrongClient:
    def __init__(self, ip='127.0.0.1', port=48062):
        self.ip = ip
        self.port = port

        self.isRunning = False

        self.sock = socket.socket()
        self.listener_thread = Thread(target=self.main_listener)
        self.message_pool = MessagePool()
        self.request_pool = MessagePool()

    # Самые базовые команды
    # =========================================
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

    def send_message(self, message, need_answer=True):
        self.msend(message.getBytes())
        if need_answer:
            self.request_pool.addMessage(message)

    # Относительно вспомогательные команды
    # =========================================
    def send_hello(self):
        bdata = uuid.UUID(baseCommands.JSON_PROTOCOL_FORMAT).bytes
        self.send(bdata)
        answer = self.recv(16, timeout=3)
        if answer != bdata:
            raise TypeError('Удалённый сервер не согласовал тип протокола')

    def protocol_compatible_req(self):
        msg = Message.command(baseCommands.PROTOCOL_COMPATIBLE)
        self.send_message(msg, need_answer=False)

    def protocol_compatible_handler(self, msg):
        # TODO: тут как-то надо обработать поддержиываемую версию протокола.
        # надо ещё понять откуда её взять
        pass

    def exec_command(self, command):
        command(self)

    def main_listener(self):
        while self.isRunning:
            answer = self.mrecv()
            if answer is not None:
                print(f'Msg JSON receeved: {answer}')
                msg = Message.fromString(answer)
                print(f'Msg received: {msg}')
                if msg.getId() not in self.request_pool:
                    # TODO Это команда с той стороны, её нужно прям тут и обработать!
                    if msg.getCommand() == baseCommands.PROTOCOL_COMPATIBLE:
                        self.protocol_compatible_handler(msg)
                else:
                    # Это команда / ответ, который нужно обработать
                    self.message_pool.addMessage(msg)

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
        self.protocol_compatible_req()

        self.isRunning = True
        self.listener_thread.start()

    def finish(self):
        self.isRunning = False
        content = dict(
            code=1,
            description='Bye bye!'
        )
        msg = Message.command(baseCommands.CLOSE_CONNECTION)
        msg.setContent(content)
        self.send_message(msg)
