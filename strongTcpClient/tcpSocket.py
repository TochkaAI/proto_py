from strongTcpClient.worker import TcpWorker
from strongTcpClient.connection import Connection
from strongTcpClient.logger import write_info


class TcpSocket(TcpWorker):
    '''сущность которая может подключится к серверу образовав тем самым конекцию,
        для дальнейшего обмена сообщениями'''
    def connect(self):
        ''' Порядок установки соединения '''
        connection = Connection(self)
        try:
            connection.connect((self.ip, self.port))
        except ConnectionRefusedError as ex:
            write_info('Не удалось, установить соединение, удалённый сервер не доступен')
            return
        self.start(connection)
        self.connection_pool.addConnection(connection)
        return connection

    def disconnect(self):
        self.finish_all(0, 'Good bye!')
