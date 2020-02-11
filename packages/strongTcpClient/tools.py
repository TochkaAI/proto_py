'''Модуль со всяческими вспомогательными функциями'''
import datetime
from uuid import UUID

from .badSituations import NotImplementedCommand


def tryUuid(uuid):
    '''определяет является ли нечто уидом, в случае успеха возвращает строку :)'''
    try:
        return str(UUID(str(uuid)))
    except ValueError as ex:
        return None


def get_time_from_int(int_tetime):
    '''конвертирует плюсовое представление таймстампа в питоновский DateTime'''
    return datetime.datetime.fromtimestamp(int_tetime / 1e3)

