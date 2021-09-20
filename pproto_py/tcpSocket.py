import time
from threading import Thread

from .config import RECONNECT_TIME_WAIT
from .connection import Connection
from .tcpWorker import TcpWorker
from .logger import logger


class TcpSocket(TcpWorker):
    """
    Сущность, которая может подключится к серверу образовав тем самым конекцию,
    для дальнейшего обмена сообщениями
    """
    def __init__(self, ip, port, client_commands, client_command_impl):
        super(TcpSocket, self).__init__(ip, port, client_commands, client_command_impl)

        self.connection_handler = None
        self.restoring_handler = None

    def start(self, connect_handler=None, restore_handler=None, disconnect_handler=None):
        self.connection_handler = connect_handler
        self.restoring_handler = restore_handler
        self.set_disconnection_handler(self.get_disconnect_handler(disconnect_handler))

        self.connect()
        if not self.get_current_connection():
            reconnecting_thread = Thread(target=self.__create_initial_connection)
            reconnecting_thread.daemon = True
            reconnecting_thread.start()

    def __create_initial_connection(self):
        while True:
            time.sleep(RECONNECT_TIME_WAIT)
            if self.connect():
                return

    def connect(self):
        """ Порядок установки соединения """
        connection = Connection(self)
        try:
            if not connection.connect((self.ip, self.port)):
                return None
            self.run_connection(connection)
        except (TimeoutError, TypeError) as ex:
            logger.info(str(ex))
            return None

        if self.connection_handler:
            self.connection_handler(connection)

        return connection

    def disconnect(self):
        self.finish_all(0, '1be0a2ad-9673-4dca-8b31-895f7986c834', 'Good bye!')

    def get_disconnect_handler(self, user_handler):
        def inner_handler(connection: Connection):
            if user_handler:
                user_handler(connection)
            connection.start_reconnecting(self.get_connected_restored_handler(), RECONNECT_TIME_WAIT)
        return inner_handler

    def get_current_connection(self):
        return self.connection_pool.get_first_connection()

    def connected_handler(self):
        if self.connection_handler:
            self.connection_handler(self.get_current_connection())

    def get_connected_restored_handler(self):
        def inner_handler(connection: Connection):
            if self.restoring_handler:
                self.restoring_handler(connection)
        return inner_handler
