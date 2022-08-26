"""Файл содержащий реализации исключений для всевозможных нештатных ситуаций"""


class ProtocolIncompatibleEx(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class UnknownCommandSend(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class UnknownCommandReceived(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class NotImplementedCommand(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class NotConnectionException(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class MessageStatusFailed(BaseException):
    def __init__(self, msg, info):
        self.failed_msg = msg
        super().__init__(info)


class MessageStatusError(BaseException):
    def __init__(self, msg, info):
        self.error_msg = msg
        super().__init__(info)
