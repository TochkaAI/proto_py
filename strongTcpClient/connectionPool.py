class ConnectionPool(dict):
    def __init__(self):
        pass

    def addConnection(self, connection):
        self[connection.getpeername()] = connection

    def info(self):
        names = [f'{i}:{j}' for i, j in self.items()]
        return '\n\r'.join(names)
