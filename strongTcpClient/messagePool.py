class MessagePool(dict):
    def __init__(self):
        pass

    def addMessage(self, message):
        self[message.get_id()] = message

    def dellMessage(self, message):
        if message.get_id() in self:
            del(self[message.get_id()])
        else:
            raise KeyError('Сообщение отсутвует в очереди')