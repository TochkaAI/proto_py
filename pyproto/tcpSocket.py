from .connection import Connection
from .worker import TcpWorker
from .logger import write_info


class TcpSocket(TcpWorker):
    """
    Сущность, которая может подключится к серверу образовав тем самым конекцию,
    для дальнейшего обмена сообщениями
    """
    def connect(self, disconect_connection_handler=None):
        """ Порядок установки соединения """
        connection = Connection(self)
        try:
            if not connection.connect((self.ip, self.port)):
                return None
            self.run_connection(connection)
        except TimeoutError as te:
            write_info(str(te))
            return None
        except TypeError as type_e:
            write_info(str(type_e))
            return None

        if disconect_connection_handler:
            self._set_disconnection_handler(disconect_connection_handler)

        return connection

    def disconnect(self):
        self.finish_all(0, 'Good bye!')
