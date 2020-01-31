'''
Список констант с существующими базовыми командами
'''
import sys

Unknown = "UNKNOWN"
Error = "ERROR"
ProtocolCompatible = "PROTOCOL_COMPATIBLE"
CloseConnection = "CLOSE_CONNECTION"


def REGISTRY_COMMAND(name, uuid):
    setattr(sys.modules[__name__], name, uuid)


REGISTRY_COMMAND(Unknown,            "4aef29d6-5b1a-4323-8655-ef0d4f1bb79d")
REGISTRY_COMMAND(Error,              "b18b98cc-b026-4bfe-8e33-e7afebfbe78b")
REGISTRY_COMMAND(ProtocolCompatible, "173cbbeb-1d81-4e01-bf3c-5d06f9c878c3")
REGISTRY_COMMAND(CloseConnection,    "e71921fd-e5b3-4f9b-8be7-283e8bb2a531")


class BaseCommand:
    @staticmethod
    def initial(*args, **kwargs):
        raise NotImplemented('не переопределена реализация методы инициализации')

    @staticmethod
    def answer(*args, **kwargs):
        pass
        # raise NotImplemented('не переопределена реализация методы обработки ответа')

    @staticmethod
    def unknown(msg):
        raise Exception('Попытка оптравки неизвестной команды!')

    @staticmethod
    def timeout():
        raise Exception('Вышло время ожидания')

    @staticmethod
    def handler(client, msg):
        raise Exception('не переопределена реализация методы обработки сообщения')


