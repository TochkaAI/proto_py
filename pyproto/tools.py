"""Модуль со вспомогательными функциями"""
import datetime
from uuid import UUID


def try_uuid(uuid):
    """Определяет являться ли входной параметр уидом, в случае успеха возвращает строку"""
    try:
        return str(UUID(str(uuid)))
    except ValueError:
        return None


def get_time_from_int(int_time):
    """Конвертирует плюсовое представление таймстампа в питоновский DateTime"""
    return datetime.datetime.fromtimestamp(int_time / 1e3)


def time_to_int(in_datetime: datetime.datetime):
    """Конвертирует datetime в плюсовое представление таймстампа"""

    # форматирование данных
    in_datetime = in_datetime.replace(tzinfo=datetime.timezone.utc)
    in_datetime -= datetime.timedelta(hours=3)

    return int(in_datetime.timestamp() * 1e3)
