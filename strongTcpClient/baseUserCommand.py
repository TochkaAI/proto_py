class BaseUserCommand:
    @staticmethod
    def initial():
        raise NotImplemented('не переопределена реализация методы инициализации')

    @staticmethod
    def answer(msg):
        raise NotImplemented('не переопределена реализация методы обработки ответа')

    @staticmethod
    def unknown(msg):
        raise Exception('Попытка оптравки неизвестной команды!')