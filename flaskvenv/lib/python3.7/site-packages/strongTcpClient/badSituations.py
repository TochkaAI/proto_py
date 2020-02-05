'''файл содержащий реализации исключений для всевозможных нештатных ситуаций

ЗЫ над этим особо пока не думал, завёл прсото чтобы различать ошибки и не кидать всегда штатный Exception'''

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