'''Модуль со всяческими вспомогательными функциями'''
import json
import datetime
from uuid import UUID, uuid4

from badSituations import NotImplementedCommand


def tryUuid(uuid):
    '''определяет является ли нечто уидом, в случае успеха возвращает строку :)'''
    try:
        return str(UUID(str(uuid)))
    except ValueError as ex:
        return None


def get_command_by_uuid(module, UUID):
    '''из опредлеённого модуля выуживает имя команды по уиду'''
    for cls in dir(module):
        obj = getattr(module, cls)
        if hasattr(obj, 'COMMAND_UUID') and getattr(obj, 'COMMAND_UUID') == UUID:
            return obj
    raise NotImplementedCommand(f'command {UUID} not implemented')


def get_command_structs(module, moduleImpl):
    '''из модуля и модуля имплементации выуживает все Классы реализации команд'''
    structs = {}
    for field in dir(module):
        if tryUuid(getattr(module, field)):
            uuid = getattr(module, field)
            structs[uuid] = (field, uuid, get_command_by_uuid(moduleImpl, uuid))
    return structs


def get_time_from_int(int_tetime):
    '''конвертирует плюсовое представление таймстампа в питоновский DateTime'''
    return datetime.datetime.fromtimestamp(int_tetime / 1e3)

