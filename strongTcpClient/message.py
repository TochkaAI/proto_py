import json
from copy import copy
from uuid import uuid4

from strongTcpClient.tools import tryUuid
from strongTcpClient.flags import MsgFlag, Type


class Message(dict):
    TCP_FIELDS = ['id', 'command', 'flags', 'content', 'protocolVersionLow',
                  'protocolVersionHigh', 'tags', 'maxTimeLife']

    def __str__(self):
        res = []

        # Определимся с типом сообщения
        type_name = Type.Unknown
        type_value = self.getType()
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

    def __init__(self, client, id=None, command=None):
        self.my_client = client
        if id is not None:
            if tryUuid(id):
                self['id'] = id
            else:
                raise ValueError('Некорректный формат идентификатора пакета')
        else:
            self['id'] = str(uuid4())

        if command is not None:
            comm_name = self.my_client.getCommandName(command)
            if comm_name is not None:
                self['command'] = command
                self['Command'] = comm_name
            else:
                raise ValueError('Неизвестный идентификатор команды')

        self['flags'] = MsgFlag()

    def getCopy(self):
        return copy(self)

    def getAnswerCopy(self):
        answer = self.getCopy()
        answer.setType(Type.Answer)
        return answer

    def setType(self, type):
        self['flags'].setFlagValue('type', type)

    def getType(self):
        return self['flags'].getFlagValue('type')

    def setContent(self, content):
        self['content'] = content
        self['flags'].setFlagValue('contentIsEmpty', 0)

    def getId(self):
        return self['id']

    def getCommand(self):
        return self['command']

    def getContent(self):
        return self.get('content')

    def setTag(self, value, num):
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

    def setMaxTimeLife(self, max_time_life):
        self['maxTimeLife'] = max_time_life

    def getMaxTimeLife(self):
        return self.get('maxTimeLife')

    def getBytes(self):
        result = dict()
        for f in Message.TCP_FIELDS:
            if f == 'flags':
                result[f] = self[f].getDigit()
            elif f in self:
                result[f] = self[f]
        return json.dumps(result).encode()

    @staticmethod
    def command(client, commandUuid):
        msg = Message(client, command=commandUuid)
        msg.setType(Type.Command)
        return msg

    @staticmethod
    def answer(client, commandUuid):
        msg = Message(client, command=commandUuid)
        msg.setType(Type.Answer)
        return msg

    @staticmethod
    def fromString(client, string_msg):
        recieved_dict = json.loads(string_msg)
        msg = Message(client, id=recieved_dict['id'], command=recieved_dict['command'])
        if recieved_dict.get('flags'):
            msg['flags'] = MsgFlag.fromDigit(recieved_dict.get('flags'))
        for key in ['content', 'tags', 'maxTimeLife', 'protocolVersionLow', 'protocolVersionHigh']:
            if recieved_dict.get(key):
                msg[key] = recieved_dict.get(key)

        return msg
