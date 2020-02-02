import socket
import time
import uuid
from threading import Thread

from strongTcpClient import baseCommands
from strongTcpClient.const import JSON_PROTOCOL_FORMAT
from strongTcpClient.message import Message
from strongTcpClient.messagePool import MessagePool
from strongTcpClient.logger import write_info
from strongTcpClient.badSituations import UnknownCommandSend


class Connection:
    '''клас обёртка вокруг питоновского TcpSocket'a
     в неём переписаны методы send recv для корректной работы по самописному протоколу'''
    def __init__(self, worker, socket_=None):
        self.message_pool = MessagePool()
        self.request_pool = MessagePool()

        self.worker = worker

        if socket_ is None:
            socket_ = socket.socket()

        self.socket = socket_

    def getpeername(self):
        '''обёртка для работы с сокетом спрятанным внутри своего лксса'''
        return self.socket.getpeername()

    def send(self, bdata):
        '''обёртка для работы с сокетом спрятанным внутри своего лксса'''
        return self.socket.send(bdata)

    def connect(self, *args, **kwargs):
        '''обёртка для работы с сокетом спрятанным внутри своего лксса'''
        self.socket.connect(*args, **kwargs)

    def close(self):
        '''обёртка для работы с сокетом спрятанным внутри своего лксса'''
        return self.socket.close()

    def msend(self, bdata):
        '''обёртка для работы с методом send для нашей реализации протокола,
        он сам в начало пакета засовывает его размер в нужном формате'''
        bdata_len = (len(bdata)).to_bytes(4, 'big')
        self.socket.send(bdata_len + bdata)

    def recv(self, buffsize, timeout=None):
        '''обёртка над методом recv, с реализацией таймаута ожидания получения
        нужен в основном для первичной установки соединения'''
        self.socket.settimeout(timeout)
        try:
            answer = self.socket.recv(buffsize)
            return answer
        except socket.timeout:
            raise TimeoutError('Удалённый сервер не ответил на приветствие в установленное время')
        finally:
            self.socket.settimeout(None)

    def mrecv(self):
        '''обёртка над методом recv, она сама считывает в начале покета его размер,
        а затем считывает нужное кол-во байт'''
        banswer_size = self.socket.recv(4)
        answer_size = int.from_bytes(banswer_size, 'big')
        ball_answer = self.socket.recv(answer_size)
        return ball_answer.decode()

    def fileno(self):
        '''обёртка над сокетом'''
        return self.socket.fileno()

    def send_hello(self):
        '''метод отправки первичного приветсвия, заключается в том,
        чтобы в битовом представлении отправить UUID протокола по которому планируем общаться'''
        bdata = uuid.UUID(JSON_PROTOCOL_FORMAT).bytes
        self.send(bdata)
        answer = self.recv(16, timeout=3)
        if answer != bdata:
            raise TypeError('Удалённый сервер не согласовал тип протокола')

    def create_command_msg(self, command_uuid):
        msg = Message.command(self, command_uuid)
        return msg

    def send_message(self, message, need_answer=False):
        '''метод отправки сущности сообщение
        во первых этот метод следит за тем чтобы отправляемая команда не было в списке неизвестных
        во вторых, устанавливает сообщению в качестве конекции саму себя для дальнейшей обркботки

        если подразумевается что на сообщени должен придти ответ, то сообщение ставиться в пул запросов
        в последсвии мониторя этот пул, мы поймаем ответное сообщение
        если ответ не нужен, то сообщение в пул не добавляется'''
        if message.get_command() in self.worker.unknown_command_list:
            raise UnknownCommandSend('Попытка оптравки неизвестной команды!')

        message.set_connection(self)
        self.msend(message.get_bytes())
        write_info(f'[{self.getpeername()}] Msg JSON send: {message.get_bytes().decode()}')
        if need_answer:
            self.request_pool.add_message(message)

    def exec_command(self, command, *args, **kwargs):
        '''подразумевается что это метод для пользователя
        отправка сущности "команды" у которой реализованы соответсвующие обработчики
        по сути является обёрткой на методом send_message
        не подразумевает получение ответа'''
        msg = command.initial(self.worker, *args, **kwargs)
        self.worker.send_message(msg, self)

    def exec_command_sync(self, command, *args, **kwargs):
        '''метод для пользователя
        отправка сущности "команда", с последущией обработкой ответа в синхронном режиме'''
        msg = command.initial(self.worker, *args, **kwargs)
        self.send_message(msg, need_answer=True)

        max_time_life = msg.get_max_time_life()
        t_end = None
        if max_time_life:
            t_end = time.time() + max_time_life
        while True:
            if t_end and time.time() > t_end:
                self.request_pool.dell_message(msg)
                return command.timeout()

            if msg.get_id() in self.message_pool:
                ans_msg = self.message_pool[msg.get_id()]
                self.request_pool.dell_message(msg)
                self.message_pool.dell_message(ans_msg)

                if ans_msg.get_command() == baseCommands.UNKNOWN:
                    return command.unknown(msg)

                return command.answer(self.worker, ans_msg, *args, **kwargs)

            time.sleep(1)

    def exec_command_async(self, command, *args, **kwargs):
        '''метод для пользователя
        отправка сущности "команда", с последущией обработкой ответа в асинхронном режиме'''
        def answer_handler():
            max_time_life = msg.get_max_time_life()
            t_end = None
            if max_time_life:
                t_end = time.time() + max_time_life
            while True:
                if t_end and time.time() > t_end:
                    self.request_pool.dell_message(msg)
                    command.timeout()
                    return

                if msg.get_id() in self.message_pool:
                    ans_msg = self.message_pool[msg.get_id()]
                    self.request_pool.dell_message(msg)
                    self.message_pool.dell_message(ans_msg)

                    if ans_msg.get_command() == baseCommands.UNKNOWN:
                        command.unknown(msg)
                        return

                    command.answer(self.worker, ans_msg, *args, **kwargs)
                    return
                time.sleep(1)

        msg = command.initial(self.worker, *args, **kwargs)
        self.send_message(msg, need_answer=True)

        listener_thread = Thread(target=answer_handler)
        listener_thread.daemon = True
        listener_thread.start()
