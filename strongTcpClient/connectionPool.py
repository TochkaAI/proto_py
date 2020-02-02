'''вспоомгательный класс для хранения списка конекций внутри воркера'''
class ConnectionPool(dict):
    def __init__(self):
        pass

    def add_connection(self, connection):
        self[connection.getpeername()] = connection

    def del_connection(self, connection):
        del(self[connection.getpeername()])

    def info(self):
        names = [f'{i}:{j}' for i, j in self.items()]
        return '\n\r'.join(names)
