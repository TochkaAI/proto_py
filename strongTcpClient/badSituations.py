class ProtocolIncompatibleEx(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class UnknownCommandSend(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class NotImplementedCommand(BaseException):
    def __init__(self, msg):
        super().__init__(msg)