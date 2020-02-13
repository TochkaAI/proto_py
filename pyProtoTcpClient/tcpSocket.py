from .connection import Connection
from .worker import TcpWorker
from .logger import write_info


class TcpSocket(TcpWorker):
    '''сущность которая может подключится к серверу образовав тем самым конекцию,
        для дальнейшего обмена сообщениями'''
    def connect(self, disconect_connection_handler=None):
        ''' Порядок установки соединения '''
        connection = Connection(self)
        try:
            connection.connect((self.ip, self.port))
        except ConnectionRefusedError as ex:
            write_info('Не удалось, установить соединение, удалённый сервер не доступен')
            return
        self.start(connection)
        self.connection_pool.add_connection(connection)
        self._cmd_method_creator(connection)

        if disconect_connection_handler:
            self._set_disconnection_handler(disconect_connection_handler)

        return connection

    def disconnect(self):
        self.finish_all(0, 'Good bye!')
