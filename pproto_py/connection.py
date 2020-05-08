import json
import socket
import time
import uuid
from threading import Thread

from . import baseCommands, config
from .config import RECONNECT_TIME_WAIT
from .const import JSON_PROTOCOL_FORMAT
from .flags import MsgFlag, ExecStatus, Type
from .message import Message
from .handlerPool import HandlerPool
from .messagePool import MessagePool
from .logger import logger


class Connection:
    """
    Класс обёртка вокруг питоновского TcpSocket'a
    в нём переопределены методы send и recv в соответствии с протоколом
    """
    def __init__(self, worker, socket_=None):
        self.user_command_recorded = False

        # после установки соединения установим эти значения (необходимо для истории)
        self.hist_fileno = None
        self.hist_peername = None

        # отслеживаем состояние сокета, проверка установления соединения
        # включая авторизацию и т.п, а не просто socket.accept()
        self.__is_active = False

        # это сообщения / ответы которые пришли нам, и мы должны их обработать
        self.message_pool = MessagePool()
        # это запросы которые мы отправляли, и хотим дождаться ответа
        self.request_pool = MessagePool()
        # это список команд, который мы ожидаем принять, для синхронной обработки
        self.sync_handler_pool = HandlerPool()

        # это воркер в рамках которого была создана конекция
        self.worker = worker  # Type: TcpWorker

        # коннекция создаётся 2мя путями, либо в сервере, либо в клиенте
        # если сокет на вход не пришёл, значит из клиента, и необходимо создать сокет, который в дальнейшем
        # подключиться к серверу
        if socket_ is None:
            socket_ = socket.socket()
        # если сокет на вход пришёл, значит он из листенера сервера, уже открыт и готов к дальнейшей работе
        else:
            # сокет в конструктор должен приходить уже открытый, поэтому можно задать значения
            self.__is_active = True
            self.hist_fileno = socket_.fileno()
            self.hist_peername = socket_.getpeername()

        # в итоге не важно сервер или клиент, есть сокет с которым мы работаем
        self.socket = socket_

    def is_connected(self):
        return self.__is_active

    def getpeername(self):
        """Обёртка для работы с сокетом спрятанным внутри своего класса"""
        if self.is_connected():
            return self.socket.getpeername()
        else:
            return self.hist_peername

    def send(self, bdata):
        """Обёртка для работы с сокетом спрятанным внутри своего класса"""
        return self.socket.send(bdata)

    def connect(self, *args, **kwargs):
        """Обёртка для работы с сокетом спрятанным внутри своего класса"""
        try:
            self.socket.connect(*args, **kwargs)
        except ConnectionRefusedError as err:
            logger.info(f'Не удалось, установить соединение,'
                        f' удалённый сервер {self.worker.ip}:{self.worker.port} не доступен {str(err)}')
            self.__is_active = False
            return False
        except OSError as err:
            logger.info(f'Не удалось, установить соединение,'
                        f' удалённый сервер {self.worker.ip}:{self.worker.port} не доступен {str(err)}')
            self.socket = socket.socket()
            self.__is_active = False
            return False

        self.__is_active = True
        self.hist_fileno = self.socket.fileno()
        self.hist_peername = self.socket.getpeername()
        return True

    def close(self):
        """Обёртка для работы с сокетом спрятанным внутри своего класса"""
        self.__is_active = False
        try:
            # Сокет мог быть принудительно убит с другой стороны.
            self.socket.shutdown(socket.SHUT_RDWR)
        except Exception:
            # Тогда делать ничего не нужно, просто закрыть его
            pass

        if self.worker.disconnection_handler is not None:
            self.worker.disconnection_handler(self)

        return self.socket.close()

    def fileno(self):
        """Обёртка над сокетом"""
        return self.socket.fileno()

    def msend(self, bdata):
        """
        Обёртка для работы с методом send для реализации протокола,
        добавляет в начало пакета его размер в нужном формате
        """
        bdata_len = (len(bdata)).to_bytes(4, 'big')
        self.socket.send(bdata_len + bdata)

    def recv(self, buffsize, timeout=None):
        """
        Обёртка над методом recv, с реализацией таймаута ожидания получения.
        Нужен в основном для первичной установки соединения
        """
        self.socket.settimeout(timeout)
        try:
            answer = self.socket.recv(buffsize)
            return answer
        except socket.timeout:
            raise TimeoutError('Удалённый сервер не ответил на приветствие в установленное время')
        finally:
            self.socket.settimeout(None)

    # TODO добавить эксепшены проверять 4 байта что норм приходят
    # TODO сделать кастомный эксепшен
    def mrecv(self):
        """
        Обёртка над методом recv, она сама считывает в начале пакета его размер,
        а затем считывает нужное кол-во байт
        """
        b_answer_size = self.socket.recv(4)
        answer_size = int.from_bytes(b_answer_size, 'big')
        data = bytearray()
        while len(data) < answer_size:
            data_frame = self.socket.recv(answer_size - len(data))
            # if not data_frame:
            #     raise Exception('Unexpected end of message')
            data.extend(data_frame)
        decoded = data.decode()
        return decoded

    def start(self):
        """
        После установки TCP соединения клиент отправляет на сокет сервера 16 байт (обычный uuid).
        Это сигнатура протокола.
        Строковое представление сигнатуры для json формата: "fea6b958-dafb-4f5c-b620-fe0aafbd47e2".
        Если сервер присылает назад этот же uuid, то успешно установлено соединение
        """
        self.send_hello()
        # После того как сигнатуры протокола проверены клиент и сервер отправляют друг другу первое сообщение -
        # ProtocolCompatible
        self.PROTOCOL_COMPATIBLE_async()

    def start_reconnecting(self, connection_restored_handler=None, wait_time=RECONNECT_TIME_WAIT):
        ip = self.worker.ip
        port = self.worker.port

        self.__is_active = False
        self.socket = socket.socket()

        def reconnecting_loop():
            while True:
                time.sleep(wait_time)
                logger.info(f'[{self.getpeername()}] Попытка переподключения к {ip}:{port}')
                if self.connect((ip, port)):
                    self.__is_active = True
                    self.worker.run_connection(self)

                    if connection_restored_handler:
                        connection_restored_handler(self)
                    return

        reconnecting_thread = Thread(target=reconnecting_loop)
        reconnecting_thread.daemon = True
        reconnecting_thread.start()

    def send_hello(self):
        """
        Метод отправки первичного приветствия, заключается в том,
        чтобы в битовом представлении отправить UUID протокола по которому планируем общаться.
        """
        b_data = uuid.UUID(JSON_PROTOCOL_FORMAT).bytes
        self.send(b_data)
        answer = self.recv(16, timeout=3)
        logger.info(f'Send hello: answer: {uuid.UUID(bytes=answer)} b_data: {uuid.UUID(bytes=b_data)}')
        if answer != b_data:
            raise TypeError(f'Удалённый сервер {self.worker.ip}:{self.worker.port} не согласовал тип протокола')

    def message_from_json(self, string_msg):
        """Метод разбора сообщения из json-строки приходящей из сети"""
        received_dict = json.loads(string_msg)
        msg = Message(self, id_=received_dict['id'], command_uuid=received_dict['command'])
        if received_dict.get('flags'):
            msg['flags'] = MsgFlag.from_digit(received_dict.get('flags'))
        for key in ['content', 'tags', 'maxTimeLife', 'PROTOCOL_VERSION_LOW', 'PROTOCOL_VERSION_HIGH']:
            if received_dict.get(key):
                msg[key] = received_dict.get(key)

        return msg

    def create_command(self, command: baseCommands.BaseCommand) -> Message:
        """Метод создаёт Message с типом Команда и заданным UUID команды"""
        msg = Message.command(self, command.COMMAND_UUID)
        return msg

    def create_event(self, command: baseCommands.BaseCommand) -> Message:
        """Метод создаёт Message с типом Событие и заданным UUID команды"""
        msg = Message.event(self, command.COMMAND_UUID)
        return msg

    def start_catching_command(self, command: baseCommands.BaseCommand):
        self.sync_handler_pool.add_command(command)

    def send_message(self, message, need_answer=False):
        """
        Метод отправки сущности сообщение, во-первых, этот метод следит за тем чтобы отправляемой команды не было в
        списке неизвестных. во-вторых, устанавливает сообщению в качестве конекции саму себя для дальнейшей обработки.

        Если подразумевается что на сообщение должен прийти ответ, то сообщение ставиться в пул запросов
        и в последствии мониторит этот пул мы поймаем ответное сообщение
        если ответ не нужен, то сообщение в пул не добавляется
        """
        if message.get_command() in self.worker.unknown_command_list:
            logger.info(f'[{message.my_connection.getpeername()}] Попытка оптравки неизвестной команды!')
            return

        try:
            message.set_connection(self)
            if need_answer:
                self.request_pool.add_message(message)
            self.msend(message.get_bytes())
            logger.info(f'[{self.getpeername()}] Msg send: {self.message_from_json(message.get_bytes().decode())}')
        except Exception as err:
            logger.error(f'Error: {err}, cant send message: {self.message_from_json(message.get_bytes().decode())}')

    def max_time_life_prolongation(self, message_id, command_id, sec_to_add):
        msg = self.request_pool.get_message(message_id)
        if not msg or msg.get_command() != command_id:
            raise Exception('Попытка продлить время несуществубщей команды')
        msg.set_max_time_life(msg.get_max_time_life() + sec_to_add)

    def exec_command(self, command, *args, **kwargs):
        """
        Подразумевается что это метод для пользователя.
        Отправка сущности "команды", у которой реализованы соответствующие обработчики.
        Является обёрткой над методом send_message, не подразумевает получение ответа
        """
        msg = command.initial(self, *args, **kwargs)
        self.send_message(msg, need_answer=False)

    def exec_command_sync(self, command, *args, **kwargs):
        """
        Метод для пользователя
        отправка сущности "команда", с последующей обработкой ответа в синхронном режиме
        """
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

                if ans_msg.get_status() == ExecStatus.Success:
                    return command.answer(ans_msg)
                elif ans_msg.get_status() == ExecStatus.Failed:
                    return command.answer_fail(ans_msg)
                elif ans_msg.get_status() == ExecStatus.Error:
                    return command.answer_error(ans_msg)

            # TODO переделать, первую секунду ждём, часто, а потом медленее и медленее
            time.sleep(0.2)

    def exec_command_async(self, command, *args, **kwargs):
        """
        Метод для пользователя
        отправка сущности "команда", с последующей обработкой ответа в асинхронном режиме
        """
        def answer_handler():
            time_of_start = time.time()
            time_of_end = time_of_start + (msg.get_max_time_life() or config.MAX_TIMEOUT_SEC)
            while True:
                if time.time() > time_of_end:
                    # время выполнения могло быть сдвинуто по инициативе другой стороны,
                    # тогда у сообщения изменится параметр max_tile_life, пересчитываем его ещё раз
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

    def catch_handler(self, command):
        self.sync_handler_pool.add_command(command)

        time_of_start = time.time()
        time_of_end = time_of_start + config.MAX_TIMEOUT_SEC
        while True:
            if time.time() > time_of_end:
                raise TimeoutError

            msg = self.message_pool.find_by_command(command)
            if msg:
                self.sync_handler_pool.remove_command(command)
                return command.handler_sync(msg)

            time.sleep(0.5)
