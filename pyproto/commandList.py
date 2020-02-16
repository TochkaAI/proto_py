"""вспомогательная структура для хранения списка доступных команд"""
from .badSituations import NotImplementedCommand
from .tools import tryUuid


class CommandList(dict):
    @staticmethod
    def get_command_by_uuid(module, UUID):
        """из опредлеённого модуля выуживает имя команды по уиду"""
        for cls in dir(module):
            obj = getattr(module, cls)
            if hasattr(obj, 'COMMAND_UUID') and getattr(obj, 'COMMAND_UUID') == UUID:
                return obj
        raise NotImplementedCommand(f'command {UUID} not implemented')

    def __init__(self, module, moduleImpl):
        """в конструктор передаётся модуль со списком команд и модуль со списком реализаций"""
        super().__init__(self)
        for field in dir(module):
            if tryUuid(getattr(module, field)):
                uuid = getattr(module, field)
                # 0 - CommandName
                # 1 - CommandUUID
                # 2 - CommandRealisation
                self[uuid] = (field, uuid, CommandList.get_command_by_uuid(moduleImpl, uuid))

    def get_command_impl(self, commandUuid):
        """по ууид команды получить её реализацию"""
        return self[commandUuid][2]

    def get_command_name(self, commandUuid):
        """По UUID команды получаем Имя команды"""
        if commandUuid in self:
            return self[commandUuid][0]
        return None

