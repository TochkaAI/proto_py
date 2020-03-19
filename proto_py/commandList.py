"""Вспомогательная структура для хранения списка доступных команд"""
from . import baseCommands
from .badSituations import NotImplementedCommand


class CommandList(dict):
    @staticmethod
    def get_command_by_uuid(module, uuid):
        """Из определённого модуля получает имя команды по UUID"""
        for cls in dir(module):
            obj = getattr(module, cls)
            if hasattr(obj, 'COMMAND_UUID') and getattr(obj, 'COMMAND_UUID') == uuid:
                return obj
        raise NotImplementedCommand(f'command {uuid} not implemented')

    def __init__(self, module, module_impl):
        """В конструктор передаётся модуль со списком команд и модуль со списком реализаций"""
        super().__init__(self)
        for field in dir(module):
            obj = getattr(module, field)
            if isinstance(obj, baseCommands.REGISTRY_COMMAND):
                uuid = obj.uuid
                # 0 - CommandName
                # 1 - CommandUUID
                # 2 - CommandRealisation
                self[uuid] = (obj.name, uuid, CommandList.get_command_by_uuid(module_impl, uuid))

    def get_command_impl(self, command_uuid):
        """По UUID команды получить её реализацию"""
        return self[command_uuid][2]

    def get_command_name(self, command_uuid):
        """По UUID команды получаем Имя команды"""
        if command_uuid in self:
            return self[command_uuid][0]
        return None
