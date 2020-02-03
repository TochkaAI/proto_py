import uuid
from threading import Thread

from strongTcpClient.logger import write_info
from strongTcpClient import baseCommands
from strongTcpClient import baseCommandsImpl
from strongTcpClient.baseCommandsImpl import ProtocolCompatibleCommand, CloseConnectionCommand, UnknownCommand
from strongTcpClient.connectionPool import ConnectionPool
from strongTcpClient.message import Message
from strongTcpClient.tools import get_command_structs
from strongTcpClient.const import JSON_PROTOCOL_FORMAT


class TcpWorker:
    '''Главная сущность осуществляющая основную логику общения между клиентами в рамках оговоренного протокола'''
    def __init__(self, ip, port, client_commands, client_command_impl):
        self.ip = ip
        self.port = port

        self.connection_pool = ConnectionPool()
        self.disconnection_handler = None

        self.base_commands_list = get_command_structs(baseCommands, baseCommandsImpl)
        self.user_commands_list = get_command_structs(client_commands, client_command_impl)

        self.unknown_command_list = []

    def _set_disconnection_handler(self, handler):
        '''если пользователь пожилает задать обработчик на разрыв соеднинения то присвоем его значение тут'''
        self.disconnection_handler = handler

    def get_command_name(self, commandUuid):
        '''По UUID команды получаем Имя команды'''
        commands_list = {**self.base_commands_list, **self.user_commands_list}
        if commandUuid in commands_list:
            return commands_list[commandUuid][0]
        return None

    def base_commands_handlers(self, msg):
        '''обработки базовых команд'''
        if msg.get_command() == baseCommands.PROTOCOL_COMPATIBLE:
            ProtocolCompatibleCommand.handler(self, msg)
        elif msg.get_command() == baseCommands.UNKNOWN:
            UnknownCommand.handler(self, msg)
        elif msg.get_command() == baseCommands.CLOSE_CONNECTION:
            CloseConnectionCommand.handler(self, msg)

    def user_commands_handlers(self, msg):
        '''обработка пользовательских команд'''
        # TODO: надо добавить прверку здесь на существование такой команды и в ответ отправлять UnknownCommand
        command = self.user_commands_list[msg.get_command()][2]
        command.handler(msg.my_worker, msg)

    def start_listening(self, connection):
        '''эта команда для конекции запускает бесконечный цикл прослушивания сокета'''
        thread = Thread(target=self.command_listener, args=(connection,))
        thread.daemon = True
        thread.start()

    def command_listener(self, connection):
        '''метод запускается в отдельном потоке и мониторит входящие пакеты
        пытается их распарсить и выполнить их соответсвующу обработку'''
        while True:
            answer = connection.mrecv()
            if answer:
                write_info(f'[{connection.getpeername()}] Msg JSON receeved: {answer}')
                msg = Message.from_string(connection, answer)
                write_info(f'[{connection.getpeername()}] Msg received: {msg}')
                # Это команда с той стороны, её нужно прям тут и обработать!
                if msg.get_id() not in connection.request_pool:
                    if msg.get_command() in self.base_commands_list:
                        self.base_commands_handlers(msg)
                    else:
                        self.user_commands_handlers(msg)
                # Это ответы, который нужно обработать
                else:
                    connection.message_pool.add_message(msg)
            else:
                # ЭТО означает что сервер разорвал соединение! о боги! это было так просто, почему яя этого не знал?
                break
        # соответственно если я тут, значит у нас произошёл разрыв соединения
        self.connection_pool.del_connection(connection)
        connection.close()
        if self.disconnection_handler is not None:
            self.disconnection_handler(connection)

    def start(self, connection):
        '''функция которая выполняет стандартный сценарий, сразу после образования Tcp соединения'''
        self.connection_pool.add_connection(connection)
        ''' После установки TCP соединения клиент отправляет на сокет сервера 16 байт (обычный uuid).
                    Это сигнатура протокола. Строковое представление сигнатуры для json формата: "fea6b958-dafb-4f5c-b620-fe0aafbd47e2".
                    Если сервер присылает назад этот же uuid, то все ОК - можно работать'''
        connection.send_hello()
        ''' После того как сигнатуры протокола проверены клиент и сервер отправляют друг другу первое сообщение - 
            ProtocolCompatible.'''
        connection.exec_command_async(ProtocolCompatibleCommand)
        self.start_listening(connection)

    def finish_all(self, code, description):
        '''функция завершает все соединения предварительно отправив команду CloseConnection'''
        for conn in self.connection_pool.values():
            perr_name = conn.getpeername()
            conn.exec_command_sync(CloseConnectionCommand, code, description)
            conn.close()
            write_info(f'[{perr_name}] Disconect from host')
