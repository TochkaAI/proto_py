class MessagePool(dict):
    def __init__(self):
        pass

    def addMessage(self, message):
        self[message.getId()] = message

    def dellMessage(self, message):
        if message.getId() in self:
            del(self[message.getId()])
        else:
            raise KeyError('Сообщение отсутвует в очереди')