"""вспомогательный класс, для хранения списка входящих или исходящих сообщений, для дальнейшей обработки хендлерами"""
from .message import Message


class MessagePool(dict):
    def __init__(self):
        pass

    def add_message(self, message: Message):
        self[message.get_id()] = message

    def dell_message(self, message):
        if message.get_id() in self:
            del(self[message.get_id()])
        else:
            raise KeyError('Сообщение отсутвует в очереди')

    def get_message(self, message_id) -> Message:
        return self.get(message_id)
