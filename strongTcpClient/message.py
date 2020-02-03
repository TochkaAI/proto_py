import json
from copy import copy
from uuid import uuid4

from strongTcpClient.badSituations import NotConnectionException
from strongTcpClient.logger import write_info
from strongTcpClient.tools import tryUuid
from strongTcpClient.flags import MsgFlag, Type


class Message(dict):
    '''Объект серриализация которого "летает" по сети
    он хранит в себе всю необходимую информаци о пакете который мы хотим отправить по сети
    Ид
    Тип
    Команду
    Контент
    Тэги
    Флаги
    Мин\Макс время жизни
    '''
    TCP_FIELDS = ['id', 'command', 'flags', 'content', 'protocolVersionLow',
                  'protocolVersionHigh', 'tags', 'maxTimeLife']

    def __str__(self):
        '''Метод для серриализации в строку для записи объекта в логах'''
        res = []

        # Определимся с типом сообщения
        type_name = Type.Unknown
        type_value = self.get_type()
        if type_value == Type.Command:
            type_name = 'Command'
        elif type_value == Type.Answer:
            type_name = 'Answer'
        elif type_value == Type.Event:
            type_name = 'Event'
        res.append(f'Type: {type_name}')

        for field in self:
            if field in ['command']: continue
            res.append(f'{field}: {self[field]}')
        return ', '.join(res)

    def __init__(self, connection, id=None, command=None):
        self.my_worker = connection.worker
        self.my_connection = connection
        # ид или создаётся, если это инициализация нового сообщения, или задаётся, если это парсинг сообщения из сети
        if id is not None:
            if tryUuid(id):
                self['id'] = id
            else:
                raise ValueError('Некорректный формат идентификатора пакета')
        else:
            self['id'] = str(uuid4())

        # если при создании передан уид команды, сразу проверим зарегистрирована ли такая команда,
        # и пропишем всю информацию в объекте
        if command is not None:
            comm_name = self.my_worker.get_command_name(command)
            if comm_name is not None:
                self['command'] = command
                self['Command'] = comm_name
            else:
                raise ValueError('Неизвестный идентификатор команды')

        # так же месседж не может существовать без флагов, при создании они инициализируются дефолтными значениями
        self['flags'] = MsgFlag()

    '''Кучка сеттеров и геттеров, для более симпатичного обращения со стороны пользователя'''
    '''==================================================================================='''
    def set_connection(self, conn):
        self.my_connection = conn

    def get_answer_copy(self):
        answer = copy(self)
        answer.set_type(Type.Answer)
        return answer

    def set_type(self, type):
        self['flags'].set_flag_value('type', type)

    def get_type(self):
        return self['flags'].get_flag_value('type')

    def set_content(self, content):
        self['content'] = content
        self['flags'].set_flag_value('contentIsEmpty', 0 if content else 1)

    def set_protocol_version_low(self, version):
        self['protocolVersionLow'] = version

    def set_protocol_version_high(self, version):
        self['protocolVersionHigh'] = version

    def get_id(self):
        return self['id']

    def get_command(self):
        return self['command']

    def get_content(self):
        return self.get('content')

    def set_tag(self, value, num):
        tags = self.get('tags')
        if not tags:
            tags = [0] * (num+1)
            tags[num] = value
            self['tags'] = tags
            return

        if len(tags) > num:
            tags[num] = value
        else:
            tags += [0]*(num - len(tags) + 1)
            tags[num] = value

    def tag(self, num):
        if len(self.get('tags')) > num:
            return self.get('tags')[num]
        # TODO сделать логирование ошибочного поведения
        return 0

    def set_max_time_life(self, max_time_life):
        self['maxTimeLife'] = max_time_life

    def get_max_time_life(self):
        return self.get('maxTimeLife')

    def get_bytes(self):
        result = dict()
        for f in Message.TCP_FIELDS:
            if f is None:
                continue
            if f == 'flags':
                result[f] = self[f].get_digit()
            elif f in self:
                result[f] = self[f]
        return json.dumps(result).encode()
    '''===========Конец кучки сеттеров и геттеров========================================='''
    '''==================================================================================='''

    def send_message(self):
        '''В случае если нужно отправить ответ на команду, у нас есть все данные и о воркере и о конеции
        можно использовать метод send_message от объекта Message
        В ином случае, нужно отправлять сообщение используя метод Connection::send_message'''
        if self.get_type() == Type.Answer and self.my_connection is not None:
            self.my_connection.msend(self.get_bytes())
            write_info(f'[{self.my_connection.getpeername()}] Msg JSON send: {self.get_bytes().decode()}')
        else:
            raise NotConnectionException('отсутсвует коннекцию, отправка невозможна')

    '''кучка статических методов для создания наиболее популярных типов месседжов
    с некими пресетами свойств(флагов, типов, контентов и т.п.'''
    @staticmethod
    def command(connection, command_uuid):
        '''Статический метод создания месседжа с типом команды'''
        msg = Message(connection, command=command_uuid)
        msg.set_type(Type.Command)
        return msg

    @staticmethod
    def answer(connection, command_uuid):
        '''Статический метод создания месседжа с типом ответ'''
        msg = Message(connection, command=command_uuid)
        msg.set_type(Type.Answer)
        return msg
    '''Конец кучки'''

    @staticmethod
    def from_string(connection, string_msg):
        '''статический медо дессериализации меседжа из json строки приходящей из "сети"'''
        # TODO перенести этот метод или в воркера или в конекцию
        recieved_dict = json.loads(string_msg)
        msg = Message(connection, id=recieved_dict['id'], command=recieved_dict['command'])
        if recieved_dict.get('flags'):
            msg['flags'] = MsgFlag.from_digit(recieved_dict.get('flags'))
        for key in ['content', 'tags', 'maxTimeLife', 'protocolVersionLow', 'protocolVersionHigh']:
            if recieved_dict.get(key):
                msg[key] = recieved_dict.get(key)

        return msg
