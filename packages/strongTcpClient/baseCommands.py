'''
Список констант с существующими базовыми командами
'''
import sys

from .logger import write_info

Unknown = "UNKNOWN"
Error = "ERROR"
ProtocolCompatible = "PROTOCOL_COMPATIBLE"
CloseConnection = "CLOSE_CONNECTION"


# Хитрая магия, функция регистрирует внутри модуля переменные с именем описанным выше,
# для удобного пользования в дальнейшем
def REGISTRY_COMMAND(name, uuid):
    setattr(sys.modules[__name__], name, uuid)


# а именно такой формат записи нужен для удобной сверки с плюсами по средсвам ctrl+f
REGISTRY_COMMAND(Unknown,            "4aef29d6-5b1a-4323-8655-ef0d4f1bb79d")
REGISTRY_COMMAND(Error,              "b18b98cc-b026-4bfe-8e33-e7afebfbe78b")
REGISTRY_COMMAND(ProtocolCompatible, "173cbbeb-1d81-4e01-bf3c-5d06f9c878c3")
REGISTRY_COMMAND(CloseConnection,    "e71921fd-e5b3-4f9b-8be7-283e8bb2a531")


class BaseCommand:
    '''Шаблон реализации всех команд
    чтобы зарегестрировать в воркере свою команду необходимо унаследоваться от этого класса и
     реализвать необходимые команды
     Пример реализации можно посмотреть в файле baseCommandsImlp там на базе этого класса реализованы
     базовые команды протокола'''
    @staticmethod
    def initial(connection, *args, **kwargs):
        '''метод вызывается перед отправкой любой команды, по сути он должен вернуть сформированный message
        для последующей отправки'''
        raise NotImplemented('не переопределена реализация методы инициализации')

    @staticmethod
    def answer(msg):
        '''метод обработчик, срабатывает в случае когда на команду приходит ответ, с тем же идентификатором
        надо понимать что сюда мы можем попасть с сообщеним типа Command и Answer'''
        pass
        # raise NotImplemented('не переопределена реализация методы обработки ответа')

    @staticmethod
    def handler(msg):
        '''метод обработчик входящей команды, идентификатор которой не найден в списке запросов
        тоесть скорее всего это значит что вторая сторона, отправила команду
        но так же сюда можно попасть по какой либо ошибке.
        так же как и в обработчике answer сюда омжно попасть с типом и Command и Answer'''
        raise Exception('не переопределена реализация методы обработки сообщения')

    @staticmethod
    def unknown(msg):
        '''обработчик на ситуацию когда в ответ на команду приходит сообщение о том что данная команда неизвестна'''
        write_info(f'[{msg.my_connection.getpeername()}] Команда неизвестна для удалённого клиента! {msg.get_id()}')
        # raise Exception('Команда неизвестна для удалённого клиента!')

    @staticmethod
    def timeout(msg):
        '''если в сообщение задать максимальное время выполнения команды,
        в случае истечения времени сработает этот обработкич'''
        raise Exception('Вышло время ожидания')


