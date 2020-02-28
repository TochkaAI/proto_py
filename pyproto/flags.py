"""Список namespace'ов для описания существующих типов флагов"""


class SocketType:
    Unknown = 0
    Local = 1
    Tcp = 2
    Udp = 3


class SerializationFormat:
    BProto = 0      # Бинарный формат
    Json = 1        # Json формат
    # LastFormat = 7 Предполагается, что будет не больше 8 форматов


class Type:
    Unknown = 0
    Command = 1     # Сообщение-команда. Это может быть сообщение с командой
                    # на выполнение действия, либо это может быть запрос
                    # на получение данных. Предполагается, что в ответ
                    # на данное сообщение придет сообщение с типом Answer.
    Answer = 2      # Ответ на сообщением с типом Command.
    Event = 3       # Данный тип сообщения похож на Command, но не предполагает
                    # получения ответа (Answer). Он используется для рассылки
                    # широковещательных сообщений о событиях


class ExecStatus:
    Unknown = 0
    Success = 1     # Сообщение было обработано успешно и содержит корректные
                    # ответные данные.
    Failed = 2      # Сообщение не было обработано успешно, но результат
                    # не является ошибкой.
                    # В данном случае сообщение (Message) будет содержать
                    # данные в формате communication::data::MessageFailed.
    Error = 3       # При обработке сообщения произошла ошибка, и в качестве
                    # ответа отправляется сообщения с описанием причины ошибки.
                    # В данном случае сообщение (Message) будет содержать
                    # данные в формате communication::data::MessageError


class Priority:
    High = 0
    Normal = 1
    Low = 2
    # Reserved = 3


class Compression:
    NoneCompression = 0
    Zip = 1
    Lzma = 2
    Ppmd = 3
    Disable = 7     # Используется в тех случаях когда нужно явно запретить
                    # сжатие сообщения при его отправке в TCP сокет.
                    # Это может потребоваться когда контент изначально сжат,
                    # например, при отправке JPG, PNG, и прочих подобных
                    # форматов


class FlagField:
    """Вспомогательная структура для хранения информации о конкретном флаге"""
    def __init__(self, name, size, value):
        self.name = name
        self.size = size
        self.value = value


class MsgFlag:
    """Структура для хранения информации о всех флагах сообщения"""
    def __str__(self):
        return str(self.get_digit())

    def __init__(self):
        self.values = [
            # 1 байт
            FlagField('type', 3, Type.Unknown),
            FlagField('execStatus', 3, ExecStatus.Unknown),
            FlagField('priority', 2, Priority.Normal),

            # 2 байт
            FlagField('compression', 3, Compression.Disable),
            FlagField('tagsIsEmpty', 1, 0),
            FlagField('maxTimeLifeIsEmpty', 1, 0),
            FlagField('contentIsEmpty', 1, 1),
            FlagField('reserved2', 2, 0),

            # 3 байт
            FlagField('reserved3', 8, 0),

            # 4 байт
            FlagField('contentFormat', 3, SerializationFormat.Json),
            FlagField('reserved4', 4, 0),
            FlagField('flags2IsEmpty', 1, 0),
        ]

    def set_flag_value(self, name, value):
        """Установить значение конкретного флага, принимает имя и значение, проверяет допустимую величину для флага"""
        for f in self.values:
            if f.name == name:
                if 2 ** f.size <= value:
                    raise ValueError('Превышено допустимое значение для флага')
                f.value = value

    def get_flag_value(self, name) -> int:
        """Получение значения флага, по имени флага"""
        for f in self.values:
            if f.name == name:
                return f.value

    def get_digit(self) -> int:
        """Преобразует значение структуры хранения данных о флаге в число, которое потом можно конвертировать
        в байтовое представление и отправить по сети"""
        res = ''
        for field in reversed(self.values):
            # число значения флага превращает в бинарное представление с ведущими нулями
            res += bin(field.value)[2:].zfill(field.size)
        # из строки вида "01010101" получаем число
        return int(res, 2)

    @staticmethod
    def from_digit(digit):
        """Из числа преобразует в структуру хранения данных флагов
        операция обратная операции get_digit"""
        b_string = bin(digit)[2:].zfill(8 * 4)
        flag = MsgFlag()
        for f in reversed(flag.values):
            f.value = int(b_string[0:f.size], 2)
            b_string = b_string[f.size:]
        return flag
