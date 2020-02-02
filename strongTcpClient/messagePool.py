'''вспомогательный класс, для хранения списка входящих или исходящих сообщений, для дальнейшей обработки хендлерами'''


class MessagePool(dict):
    def __init__(self):
        pass

    def add_message(self, message):
        self[message.get_id()] = message

    def dell_message(self, message):
        if message.get_id() in self:
            del(self[message.get_id()])
        else:
            raise KeyError('Сообщение отсутвует в очереди')