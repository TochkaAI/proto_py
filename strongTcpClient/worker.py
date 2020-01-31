import socket
import uuid
from threading import Thread

from strongTcpClient.logger import write_info
from strongTcpClient import baseCommands
from strongTcpClient import baseCommandsImpl
from strongTcpClient.baseCommandsImpl import ProtocolCompatibleCommand, CloseConnectionCommand, UnknownCommand
from strongTcpClient.connection import Connection
from strongTcpClient.connectionPool import ConnectionPool
from strongTcpClient.message import Message
from strongTcpClient.tools import tryUuid, getCommandStruct
from strongTcpClient.const import JSON_PROTOCOL_FORMAT


class TcpWorker:
    def __init__(self, ip, port, client_commands, client_command_impl):
        self.ip = ip
        self.port = port

        self.connection_pool = ConnectionPool()

        self.base_commands_list = getCommandStruct(baseCommands, baseCommandsImpl)
        self.user_commands_list = getCommandStruct(client_commands, client_command_impl)

        self.unknown_command_list = []

    def getCommandName(self, commandUuid):
        commands_list = {**self.base_commands_list, **self.user_commands_list}
        if commandUuid in commands_list:
            return commands_list[commandUuid][0]
        return None

    def send_hello(self, connection):
        bdata = uuid.UUID(JSON_PROTOCOL_FORMAT).bytes
        connection.send(bdata)
        answer = connection.recv(16, timeout=3)
        if answer != bdata:
            raise TypeError('Удалённый сервер не согласовал тип протокола')

    def base_commands_handlers(self, msg):
        # Это команда с той стороны, её нужно прям тут и обработать!
        if msg.getCommand() == baseCommands.PROTOCOL_COMPATIBLE:
            ProtocolCompatibleCommand.handler(self, msg)
        elif msg.getCommand() == baseCommands.UNKNOWN:
            UnknownCommand.handler(self, msg)
        elif msg.getCommand() == baseCommands.CLOSE_CONNECTION:
            CloseConnectionCommand.handler(self, msg)

    def user_commands_handlers(self, msg):
        command = self.user_commands_list[msg.getCommand()][2]
        command.handler(msg.my_client, msg)

    def start_listening(self, connection):
        thread = Thread(target=self.command_listener, args=(connection,))
        thread.daemon = True
        thread.start()

    def command_listener(self, connection):
        while True:
            answer = connection.mrecv()
            if answer:
                write_info(f'[{connection.getpeername()}] Msg JSON receeved: {answer}')
                msg = Message.fromString(self, answer, connection)
                write_info(f'[{connection.getpeername()}] Msg received: {msg}')
                if msg.getId() not in connection.request_pool:
                    # Это команды
                    if msg.getCommand() in self.base_commands_list:
                        self.base_commands_handlers(msg)
                    else:
                        self.user_commands_handlers(msg)
                else:
                    # Это ответы, который нужно обработать
                    connection.message_pool.addMessage(msg)

    def connect(self):
        ''' Порядок установки соединения '''
        connection = Connection(self)
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
            conn = Connection(self, sock)
            write_info(f'{conn.getpeername()} - was connected')
            self.start(conn)

            if new_client_handler:
                new_client_handler(conn)

    def listen(self, new_client_handler=None):
        serv_sock = socket.socket()
        serv_sock.bind((self.ip, self.port))
        serv_sock.listen(10)

        thread = Thread(target=self.connect_listener, args=(serv_sock, new_client_handler))
        thread.daemon = True
        thread.start()

    def start(self, connection):
        self.connection_pool.addConnection(connection)
        ''' После установки TCP соединения клиент отправляет на сокет сервера 16 байт (обычный uuid).
                    Это сигнатура протокола. Строковое представление сигнатуры для json формата: "fea6b958-dafb-4f5c-b620-fe0aafbd47e2".
                    Если сервер присылает назад этот же uuid, то все ОК - можно работать'''
        self.send_hello(connection)
        ''' После того как сигнатуры протокола проверены клиент и сервер отправляют друг другу первое сообщение - 
            ProtocolCompatible.'''
        connection.exec_command_async(ProtocolCompatibleCommand)
        self.start_listening(connection)

    def finish_all(self, code, description):
        for conn in self.connection_pool.values():
            if conn.fileno() == -1:
                continue
            perr_name = conn.getpeername()
            conn.exec_command_sync(CloseConnectionCommand, code, description)
            write_info(f'[{perr_name}] Disconect from host')
