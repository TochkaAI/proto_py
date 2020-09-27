"""Модуль с реализацией структуры комманды"""


class Command:
    """Реализация дата класса команды"""
    commands_names = []
    commands_uuids = []

    def __init__(self, name: str, command_uuid: str) -> None:
        """
        Проверяет что регистрируемые имя и id команды
        в текущем процессе регистрируется впервые

        :param name: наименование регистрируемой команды
        :param command_uuid: индетификатор команды - строковое значение uuid v4
        """
        self.name = name
        self.uuid = command_uuid
        if name in Command.commands_names:
            raise ValueError(f'Command name {name} is not unique')
        if command_uuid in Command.commands_uuids:
            raise ValueError(f'Command uuid {command_uuid} is not unique')
        Command.commands_names.append(name)
        Command.commands_uuids.append(command_uuid)
