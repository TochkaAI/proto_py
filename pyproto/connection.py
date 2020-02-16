import socket
import time
import uuid
from threading import Thread

from . import baseCommands, config
from .const import JSON_PROTOCOL_FORMAT
from .message import Message
from .messagePool import MessagePool
from .logger import write_info


class Connection:
    """клас обёртка вокруг питоновского TcpSocket'a
     в неём переписаны методы send recv для корректной работы по самописному протоколу"""
    def __init__(self, worker, socket_=None):
        # после установки соединения установим эти значение
        # подразумевается что это надо для истории
        self.hist_fileno = None
        self.hist_peername = None

        self.message_pool = MessagePool()
        self.request_pool = MessagePool()

        self.worker = worker

        if socket_ is None:
            socket_ = socket.socket()
        else:
            # сокет в конструктор должен прхиодить уже октрытый
            # по этому можно задать значения
            self.hist_fileno = socket_.fileno()
            self.hist_peername = socket_.getpeername()

        self.socket = socket_

    def is_connected(self):
        return self.fileno() != -1

    def getpeername(self):
        """обёртка для работы с сокетом спрятанным внутри своего лксса"""
        if self.is_connected():
            return self.socket.getpeername()
        else:
            return "(None, None) closed"

    def send(self, bdata):
        """обёртка для работы с сокетом спрятанным внутри своего лксса"""
        return self.socket.send(bdata)

    def connect(self, *args, **kwargs):
        """обёртка для работы с сокетом спрятанным внутри своего лксса"""
        self.socket.connect(*args, **kwargs)
        self.hist_peername = self.getpeername()
        self.hist_fileno = self.fileno()

    def close(self):
        """обёртка для работы с сокетом спрятанным внутри своего лксса"""
        return self.socket.close()

    def fileno(self):
        """обёртка над сокетом"""
        return self.socket.fileno()

    def msend(self, bdata):
        """обёртка для работы с методом send для нашей реализации протокола,
        он сам в начало пакета засовывает его размер в нужном формате"""
        bdata_len = (len(bdata)).to_bytes(4, 'big')
        self.socket.send(bdata_len + bdata)

    def recv(self, buffsize, timeout=None):
        """обёртка над методом recv, с реализацией таймаута ожидания получения
        нужен в основном для первичной установки соединения"""
        self.socket.settimeout(timeout)
        try:
            answer = self.socket.recv(buffsize)
            return answer
        except socket.timeout:
            raise TimeoutError('Удалённый сервер не ответил на приветствие в установленное время')
        finally:
            self.socket.settimeout(None)

    def mrecv(self):
        """обёртка над методом recv, она сама считывает в начале покета его размер,
        а затем считывает нужное кол-во байт"""
        banswer_size = self.socket.recv(4)
        answer_size = int.from_bytes(banswer_size, 'big')
        ball_answer = self.socket.recv(answer_size)
        return ball_answer.decode()

    def send_hello(self):
        """метод отправки первичного приветсвия, заключается в том,
        чтобы в битовом представлении отправить UUID протокола по которому планируем общаться"""
        bdata = uuid.UUID(JSON_PROTOCOL_FORMAT).bytes
        self.send(bdata)
        answer = self.recv(16, timeout=3)
        if answer != bdata:
            raise TypeError('Удалённый сервер не согласовал тип протокола')

    def create_command_msg(self, command_uuid) -> Message:
        msg = Message.command(self, command_uuid)
        return msg

    def send_message(self, message, need_answer=False):
        """метод отправки сущности сообщение
        во первых этот метод следит за тем чтобы отправляемая команда не было в списке неизвестных
        во вторых, устанавливает сообщению в качестве конекции саму себя для дальнейшей обркботки

        если подразумевается что на сообщени должен придти ответ, то сообщение ставиться в пул запросов
        в последсвии мониторя этот пул, мы поймаем ответное сообщение
        если ответ не нужен, то сообщение в пул не добавляется"""
        if message.get_command() in self.worker.unknown_command_list:
            write_info(f'[{message.my_connection.getpeername()}] Попытка оптравки неизвестной команды!')
            return
            # raise UnknownCommandSend('Попытка оптравки неизвестной команды!')

        message.set_connection(self)
        self.msend(message.get_bytes())
        write_info(f'[{self.getpeername()}] Msg JSON send: {message.get_bytes().decode()}')
        if need_answer:
            self.request_pool.add_message(message)

    def max_time_life_prolongation(self, message_id, command_id, sec_to_add):
        msg = self.request_pool.get_message(message_id)
        if not msg or msg.get_command() != command_id:
            raise Exception('Попытка продлить время несуществубщей команды')
        msg.set_max_time_life(msg.get_max_time_life() + sec_to_add)

    def exec_command(self, command, *args, **kwargs):
        """подразумевается что это метод для пользователя
        отправка сущности "команды" у которой реализованы соответсвующие обработчики
        по сути является обёрткой на методом send_message
        не подразумевает получение ответа"""
        msg = command.initial(self, *args, **kwargs)
        self.send_message(msg, need_answer=False)

    def exec_command_sync(self, command, *args, **kwargs):
        """метод для пользователя
        отправка сущности "команда", с последущией обработкой ответа в синхронном режиме"""
        msg = command.initial(self, *args, **kwargs)
        self.send_message(msg, need_answer=True)

        time_of_start = time.time()
        time_of_end = time_of_start + (msg.get_max_time_life() or config.MAX_TIMEOUT_SEC)
        while True:
            if time.time() > time_of_end:
                # время выполнения могло быть сдвинуто по инициативе другой стороны,
                # тогда у сообщения измениться параметр max_tile_life, пересчитаем его ещё разок
                time_of_end = time_of_start + (msg.get_max_time_life() or config.MAX_TIMEOUT_SEC)
                if time.time() > time_of_end:
                    self.request_pool.dell_message(msg)
                    return command.timeout(msg)

            if msg.get_id() in self.message_pool:
                ans_msg = self.message_pool.get_message(msg.get_id())
                self.request_pool.dell_message(msg)
                self.message_pool.dell_message(ans_msg)

                if ans_msg.get_command() == baseCommands.UNKNOWN:
                    return command.unknown(msg)

                return command.answer(ans_msg)

            #TODO тут можно написать модную штуку, типа первую секунду ждём, часто, а потом медленее и медленее
            time.sleep(0.2)

    def exec_command_async(self, command, *args, **kwargs):
        """метод для пользователя
        отправка сущности "команда", с последущией обработкой ответа в асинхронном режиме"""
        def answer_handler():
            time_of_start = time.time()
            time_of_end = time_of_start + (msg.get_max_time_life() or config.MAX_TIMEOUT_SEC)
            while True:
                if time.time() > time_of_end:
                    # время выполнения могло быть сдвинуто по инициативе другой стороны,
                    # тогда у сообщения измениться параметр max_tile_life, пересчитаем его ещё разок
                    time_of_end = time_of_start + (msg.get_max_time_life() or config.MAX_TIMEOUT_SEC)
                    if time.time() > time_of_end:
                        self.request_pool.dell_message(msg)
                        command.timeout(msg)
                        return

                if msg.get_id() in self.message_pool:
                    ans_msg = self.message_pool.get_message(msg.get_id())
                    self.request_pool.dell_message(msg)
                    self.message_pool.dell_message(ans_msg)

                    if ans_msg.get_command() == baseCommands.UNKNOWN:
                        command.unknown(msg)
                        return

                    command.answer(ans_msg)
                    return
                time.sleep(0.2)

        msg = command.initial(self, *args, **kwargs)
        self.send_message(msg, need_answer=True)

        listener_thread = Thread(target=answer_handler)
        listener_thread.daemon = True
        listener_thread.start()
