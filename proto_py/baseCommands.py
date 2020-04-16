"""Список констант с базовыми командами"""
from .badSituations import MessageStatusFailed, MessageStatusError
from .message import Message
from .logger import logger


Unknown = 'UNKNOWN'
Error = 'ERROR'
ProtocolCompatible = 'PROTOCOL_COMPATIBLE'
CloseConnection = 'CLOSE_CONNECTION'


class REGISTRY_COMMAND:
    commands_names = []
    commands_uuids = []

    def __init__(self, name, uuid):
        self.name = name
        self.uuid = uuid
        if name in REGISTRY_COMMAND.commands_names:
            raise ValueError(f'Command name {name} is not unique')
        if uuid in REGISTRY_COMMAND.commands_uuids:
            raise ValueError(f'Command uuid {uuid} is not unique')
        REGISTRY_COMMAND.commands_names.append(name)
        REGISTRY_COMMAND.commands_uuids.append(uuid)


# Регистрация базовых команд
UNKNOWN             = REGISTRY_COMMAND(Unknown,            "4aef29d6-5b1a-4323-8655-ef0d4f1bb79d")
ERROR               = REGISTRY_COMMAND(Error,              "b18b98cc-b026-4bfe-8e33-e7afebfbe78b")
PROTOCOL_COMPATIBLE = REGISTRY_COMMAND(ProtocolCompatible, "173cbbeb-1d81-4e01-bf3c-5d06f9c878c3")
CLOSE_CONNECTION    = REGISTRY_COMMAND(CloseConnection,    "e71921fd-e5b3-4f9b-8be7-283e8bb2a531")


class BaseCommand:
    """
    Шаблон реализации всех команд
    Чтобы зарегистрировать в воркере свою команду, необходимо наследоваться от этого класса и
    реализовать необходимые команды.
    Пример реализации расположен в файле baseCommandsImpl, где с помощью этого класса реализованы
    базовые команды протокола
    """
    COMMAND_UUID = None

    @staticmethod
    def initial(connection, *args, **kwargs):
        """
        Метод вызывается перед отправкой любой команды, он должен вернуть сформированный message
        для последующей отправки
        """
        raise NotImplemented('Initialization method not implemented yet')

    @staticmethod
    def answer(msg: Message):
        """
        Метод обработчик, срабатывает в случае, когда на команду приходит ответ, с тем же идентификатором.
        Сюда мы можем попасть с сообщение типа Command и Answer
        """
        pass

    @staticmethod
    def answer_fail(msg: Message):
        """
        Метод обработчик ответа на команду, вызывается в том случает когда отет приходит со статусом ExecStatus.Failed
        """
        raise MessageStatusFailed(msg, f'Command {msg.get_id()} was failed')

    @staticmethod
    def answer_error(msg: Message):
        """
        Метод обработчик ответа на команду, вызывается в том случает когда отет приходит со статусом ExecStatus.Failed
        """
        raise MessageStatusError(msg, f'Command {msg.get_id()} was error')

    @staticmethod
    def handler(msg: Message):
        """
        Метод обработчик входящей команды, идентификатор которой не найден в списке запросов.
        Скорее всего это значит что вторая сторона, отправила команду, но также сюда можно попасть по какой-либо ошибке.
        Так же как и в обработчике answer сюда можно попасть с типом и Command и Answer
        """
        raise Exception('Message processing method not implemented yet')

    @staticmethod
    def handler_sync(msg: Message):
        raise Exception('Message sync handler is not implemented')

    @staticmethod
    def unknown(msg: Message):
        """
        Обработчик ситуации, при которой в ответ на команду приходит сообщение о том, что данная команда неизвестна
        """
        logger.info(f'[{msg.my_connection.getpeername()}] Unknown command for remote client! {msg.get_id()}')
        # raise Exception('Команда неизвестна для удалённого клиента!')

    @staticmethod
    def timeout(msg: Message):
        """
        Если в сообщении задать максимальное время выполнения команды,
        в случае истечения времени сработает этот обработчик
        """
        raise TimeoutError('Waiting command execution timed out')

    @classmethod
    def exec_decorator(cls, connection):
        def function_template(*args, **kwargs):
            connection.exec_command(cls, *args, **kwargs)
        return function_template

    @classmethod
    def sync_decorator(cls, connection):
        def function_template(*args, **kwargs):
            return connection.exec_command_sync(cls, *args, **kwargs)
        return function_template

    @classmethod
    def async_decorator(cls, connection):
        def function_template(*args, **kwargs):
            connection.exec_command_async(cls, *args, **kwargs)
        return function_template

    @classmethod
    def sync_handler_decorator(cls, connection):
        def function_template():
            return connection.catch_handler(cls)
        return function_template
