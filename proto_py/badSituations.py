"""Файл содержащий реализации исключений для всевозможных нештатных ситуаций"""


class ProtocolIncompatibleEx(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class UnknownCommandSend(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class UnknownCommandRecieved(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class NotImplementedCommand(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class NotConnectionException(BaseException):
    def __init__(self, msg):
        super().__init__(msg)
