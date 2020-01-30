import socket
import uuid
from threading import Thread
import time

from strongTcpClient import config
from strongTcpClient.logger import write_info
from strongTcpClient import baseCommands
from strongTcpClient.connection import Connection
from strongTcpClient.connectionPool import ConnectionPool
from strongTcpClient.message import Message
from strongTcpClient.baseCommandsImpl import CloseConnectionCommand
from strongTcpClient.tools import getCommandNameList, tryUuid


class StrongClient:
    def __init__(self, ip, port, client_commands=[]):
        self.ip = ip
        self.port = port

        self.connection_pool = ConnectionPool()

        self.base_commands_list = getCommandNameList(baseCommands)
        self.user_commands_list = client_commands

        self.unknown_command_list = []

    def getCommandName(self, commandUuid):
        commands_list = self.base_commands_list + self.user_commands_list
        for comm_name in commands_list:
            value = comm_name[1]
            if tryUuid(value) and value == commandUuid:
                return comm_name[0]
        return None

    def send_message(self, message, conn, need_answer=True):
        if message.getCommand() in self.unknown_command_list:
            # TODO: наверное стоит сделать своё исключение на это дело
            raise Exception('Попытка оптравки неизвестной команды!')

        message.setConnection(conn)
        conn.msend(message.getBytes())
        write_info(f'[{conn.getpeername()}] Msg JSON send: {message.getBytes().decode()}')
        if need_answer:
            conn.request_pool.addMessage(message)

    def send_hello(self, connection):
        bdata = uuid.UUID(baseCommands.JSON_PROTOCOL_FORMAT).bytes
        connection.send(bdata)
        answer = connection.recv(16, timeout=3)
        if answer != bdata:
            raise TypeError('Удалённый сервер не согласовал тип протокола')

    def protocol_compatible_req(self, connection):
        msg = Message.command(self, baseCommands.PROTOCOL_COMPATIBLE)
        msg['protocolVersionLow'] = config.protocolVersionLow
        msg['protocolVersionHigh'] = config.protocolVersionHigh
        self.send_message(msg, connection, need_answer=False)

    def protocol_compatible_handler(self, msg):
        def protocol_compatible(versionLow, versionHigh):
            if versionHigh is None and versionLow is None:
                # Видимо ничего не надо делать
                return True
            if versionLow > versionHigh:
                return False
            if versionHigh < config.protocolVersionLow:
                return False
            if versionLow > config.protocolVersionHigh:
                return False
            return True
        if not config.checkProtocolVersion:
            return
        if not protocol_compatible(msg.get('protocolVersionLow'), msg.get('protocolVersionHigh')):
            msg = f'Protocol versions incompatible. This protocol version: {config.protocolVersionLow}-{config.protocolVersionHigh}. ' \
                  f'Remote protocol version: {msg.get("protocolVersionLow")}-{msg.get("protocolVersionHigh")}'
            self.finish(code=0, description=msg, is_async=True)
            # raise ProtocolIncompatibleEx(msg)

    def close_connection_handler(self, msg):
        self.send_message(msg.getAnswerCopy(), msg.my_connection, need_answer=False)
        msg.my_connection.isRunning = False

    def unknow_command_handler(self, msg):
        unknown_command_uid = msg.getContent().get('commandId')
        self.unknown_command_list.append(unknown_command_uid)
        for req_msg in msg.my_connection.request_pool.values():
            if req_msg.getCommand() == unknown_command_uid:
                fake_msg = Message(self, id=req_msg.getId(), command=baseCommands.UNKNOWN)
                msg.my_connection.message_pool.addMessage(fake_msg)

    def exec_command_sync(self, command, conn, *args, **kwargs):
        msg = command.initial(self, *args, **kwargs)
        self.send_message(msg, conn)

        max_time_life = msg.getMaxTimeLife()
        t_end = None
        if max_time_life:
            t_end = time.time() + max_time_life
        while True and conn.isRunning:
            if t_end and time.time() > t_end:
                conn.request_pool.dellMessage(msg)
                return command.timeout()

            if msg.getId() in conn.message_pool:
                ans_msg = conn.message_pool[msg.getId()]
                conn.request_pool.dellMessage(msg)
                conn.message_pool.dellMessage(ans_msg)

                if ans_msg.getCommand() == baseCommands.UNKNOWN:
                    return command.unknown(msg)

                return command.answer(self, ans_msg, *args, **kwargs)

            time.sleep(1)

    def exec_command_async(self, command, conn, *args, **kwargs):
        def answer_handler():
            max_time_life = msg.getMaxTimeLife()
            t_end = None
            if max_time_life:
                t_end = time.time() + max_time_life
            while True and conn.isRunning:
                if t_end and time.time() > t_end:
                    conn.request_pool.dellMessage(msg)
                    command.timeout()
                    return

                if msg.getId() in conn.message_pool:
                    ans_msg = conn.message_pool[msg.getId()]
                    conn.request_pool.dellMessage(msg)
                    conn.message_pool.dellMessage(ans_msg)

                    if ans_msg.getCommand() == baseCommands.UNKNOWN:
                        command.unknown(msg)
                        return

                    command.answer(self, ans_msg, *args, **kwargs)
                    return
                time.sleep(1)

        msg = command.initial(self, *args, **kwargs)
        self.send_message(msg, conn)

        listener_thread = Thread(target=answer_handler)
        listener_thread.start()

    def base_commands_handlers(self, msg):
        # Это команда с той стороны, её нужно прям тут и обработать!
        if msg.getCommand() == baseCommands.PROTOCOL_COMPATIBLE:
            self.protocol_compatible_handler(msg)
        elif msg.getCommand() == baseCommands.UNKNOWN:
            self.unknow_command_handler(msg)
        elif msg.getCommand() == baseCommands.CLOSE_CONNECTION:
            self.close_connection_handler(msg)

    def user_commands_handlers(self, msg):
        pass

    def start_listening(self, connection):
        thread = Thread(target=self.command_listener, args=(connection,))
        thread.start()

    def command_listener(self, connection):
        while connection.isRunning:
            answer = connection.mrecv()
            if answer:
                write_info(f'[{connection.getpeername()}] Msg JSON receeved: {answer}')
                msg = Message.fromString(self, answer, connection)
                write_info(f'[{connection.getpeername()}] Msg received: {msg}')
                if msg.getId() not in connection.request_pool:
                    # Это команды
                    if msg.getCommand() in [uuid[1] for uuid in self.base_commands_list]:
                        self.base_commands_handlers(msg)
                    else:
                        self.user_commands_handlers(msg)
                else:
                    # Это ответы, который нужно обработать
                    connection.message_pool.addMessage(msg)

        write_info(f'Disconect from host: {self.ip}:{self.port}')

    def connect(self):
        ''' Порядок установки соединения '''
        connection = Connection()
        try:
            connection.connect((self.ip, self.port))
        except ConnectionRefusedError as ex:
            write_info('Не удалось, установить соединение, удалённый сервер не доступен')
            return
        self.start(connection)
        return connection

    def connect_listener(self, serv_sock, new_client_handler):
        while True:
            sock, adr = serv_sock.accept()
            conn = Connection(sock)
            write_info(f'{conn.getpeername()} - was connected')
            self.start(conn)

            if new_client_handler:
                new_client_handler(conn)

    def listen(self, new_client_handler=None):
        serv_sock = socket.socket()
        serv_sock.bind((self.ip, self.port))
        serv_sock.listen(10)

        thread = Thread(target=self.connect_listener, args=(serv_sock, new_client_handler))
        thread.start()

    def start(self, connection):
        self.connection_pool.addConnection(connection)
        ''' После установки TCP соединения клиент отправляет на сокет сервера 16 байт (обычный uuid).
                    Это сигнатура протокола. Строковое представление сигнатуры для json формата: "fea6b958-dafb-4f5c-b620-fe0aafbd47e2".
                    Если сервер присылает назад этот же uuid, то все ОК - можно работать'''
        self.send_hello(connection)
        ''' После того как сигнатуры протокола проверены клиент и сервер отправляют друг другу первое сообщение - 
            ProtocolCompatible.'''
        self.protocol_compatible_req(connection)

        connection.isRunning = True
        self.start_listening(connection)

    def finish(self, conn, code, description, is_async=False):
        if not conn.isRunning:
            return

        if is_async:
            self.exec_command_async(CloseConnectionCommand, conn, code, description)
        else:
            self.exec_command_sync(CloseConnectionCommand, conn, code, description)
