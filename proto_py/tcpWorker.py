from threading import Thread

from .badSituations import UnknownCommandRecieved
from .commandList import CommandList
from .connection import Connection
from .logger import logger
from . import baseCommands
from . import baseCommandsImpl
from .baseCommandsImpl import CloseConnectionCommand, UnknownCommand
from .connectionPool import ConnectionPool


class TcpWorker:
    """Главная сущность осуществляющая основную логику общения между клиентами в рамках оговоренного протокола"""
    user_commands_list: CommandList
    base_commands_list: CommandList

    def __init__(self, ip, port, client_commands, client_command_impl):
        self.ip = ip
        self.port = port

        self.connection_pool = ConnectionPool()
        self.disconnection_handler = None

        self.base_commands_list = CommandList(baseCommands, baseCommandsImpl)
        self.user_commands_list = CommandList(client_commands, client_command_impl)

        self.unknown_command_list = []

    def set_disconnection_handler(self, handler):
        """Если пользователь пожелает задать обработчик на разрыв соединения, то присвоим его значение тут"""
        self.disconnection_handler = handler

    def _cmd_method_creator(self, connection):
        """Создаёт у коннекции всевозможные доступные пользовательские и базовые методы"""
        if connection.user_command_recorded:
            return
        connection.user_command_recorded = True
        for cmd in list(self.user_commands_list.values()) + list(self.base_commands_list.values()):
            setattr(connection, cmd[0] + '_exec', cmd[2].exec_decorator(connection))
            setattr(connection, cmd[0] + '_sync', cmd[2].sync_decorator(connection))
            setattr(connection, cmd[0] + '_async', cmd[2].async_decorator(connection))
            setattr(connection, cmd[0] + '_catch', cmd[2].sync_handler_decorator(connection))

    def get_command_name(self, command_uuid):
        """По UUID команды получаем Имя команды из списка базовых или из списка пользовательских"""
        return (self.base_commands_list.get_command_name(command_uuid) or
                self.user_commands_list.get_command_name(command_uuid))

    def command_handler(self, msg):
        if msg.get_command() in self.base_commands_list:
            # Обработчики базовых команд
            command = self.base_commands_list.get_command_impl(msg.get_command())
        else:
            # Обработчики пользовательских команд
            command = self.user_commands_list.get_command_impl(msg.get_command())
        # и теперь отправим обрабатывать это в отдельный поток, чтоб не тормозило получение новых команд
        thread = Thread(target=command.handler, args=(msg,))
        thread.daemon = True
        thread.start()

    def start_listening(self, connection):
        """Эта команда для конекции запускает бесконечный цикл прослушивания сокета"""
        thread = Thread(target=self.command_listener, args=(connection,))
        thread.daemon = True
        thread.start()

    def command_listener(self, connection: Connection):
        """Метод запускается в отдельном потоке и мониторит входящие пакеты
        пытается их распарсить и выполнить их соответствующую обработку"""
        while True:
            json_data = connection.mrecv()
            if json_data:
                # logger.info(f'[{connection.getpeername()}] JSON received: {json_data}')
                try:
                    msg = connection.message_from_json(json_data)  # Type: Message
                except UnknownCommandRecieved:
                    logger.info(f'[{connection.getpeername()}] Unknown msg received')
                    connection.exec_command(UnknownCommand, json_data)
                else:
                    logger.info(f'[{connection.getpeername()}] Msg  received: {msg}')
                    # Это ответы, которые нужно обработать, в синхронном или асинхронном режиме
                    if msg.get_id() in connection.request_pool or \
                            connection.sync_handler_pool.is_catching(msg.get_command()):
                        connection.message_pool.add_message(msg)
                    # Это команда с той стороны, её нужно передать в соответсвующий handler
                    else:
                        self.command_handler(msg)
            else:
                break
        # соответственно если я тут, значит у нас произошёл разрыв соединения
        self.connection_pool.del_connection(connection)
        if connection.is_connected():  # тут нужна проверка, потому что мы сами могли порвать соединение
            connection.close()

    def run_connection(self, connection: Connection):
        """Функция которая выполняет стандартный сценарий, сразу после образования Tcp соединения"""
        self.connection_pool.add_connection(connection)
        self._cmd_method_creator(connection)
        connection.start()
        self.start_listening(connection)

    def finish_all(self, code, description):
        """Функция завершает все соединения предварительно отправив команду CloseConnection"""
        for conn in list(self.connection_pool.values()):
            peer_name = conn.getpeername()
            conn.exec_command_sync(CloseConnectionCommand, code, description)
            conn.close()
            logger.info(f'[{peer_name}] Disconect from host')
