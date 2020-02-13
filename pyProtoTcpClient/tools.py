"""Модуль со всяческими вспомогательными функциями"""
import datetime
from uuid import UUID


def tryUuid(uuid):
    """определяет является ли нечто уидом, в случае успеха возвращает строку :)"""
    try:
        return str(UUID(str(uuid)))
    except ValueError as ex:
        return None


def get_time_from_int(int_time):
    """конвертирует плюсовое представление таймстампа в питоновский DateTime"""
    return datetime.datetime.fromtimestamp(int_time / 1e3)


def time_to_int(in_datetime: datetime.datetime):
    """Конвертирует datetime в плюсовое представление тайстампа"""
    return int(in_datetime.timestamp() * 1e3)
