import json
from uuid import uuid4

from strongTcpClient.tools import tryUuid, getCommandName
from strongTcpClient.flags import MsgFlag, Type


class Message(dict):
    TCP_FIELDS = ['id', 'command', 'flags', 'content']

    def __str__(self):
        res = []
        for field in self:
            if field in ['command']: continue
            res.append(f'{field}: {self[field]}')
        return ', '.join(res)

    def __init__(self, id=None, command=None):
        if id is not None:
            if tryUuid(id):
                self['id'] = id
            else:
                raise ValueError('Некорректный формат идентификатора пакета')
        else:
            self['id'] = str(uuid4())

        if command is not None:
            comm_name = getCommandName(command)
            if comm_name != 'UNKNOWN':
                self['command'] = command
                self['Command'] = comm_name
            else:
                raise ValueError('Неизвестный идентификатор команды')

        self['flags'] = MsgFlag()


    def setType(self, type):
        self['flags'].setFlagValue('type', type)

    def getType(self):
        self['flags'].getFlagValue('type')

    def setContent(self, content):
        self['content'] = content
        self['flags'].setFlagValue('contentIsEmpty', 0)

    def getBytes(self):
        result = dict()
        for f in Message.TCP_FIELDS:
            if f == 'flags':
                result[f] = self[f].getDigit()
            elif f in self:
                result[f] = self[f]
        return json.dumps(result).encode()

    @staticmethod
    def command(commandUuid):
        msg = Message(command=commandUuid)
        msg.setType(Type.Command)
        return msg

    @staticmethod
    def answer(commandUuid):
        msg = Message(command=commandUuid)
        msg.setType(Type.Answer)
        return msg

    @staticmethod
    def fromString(string_msg):
        recieved_dict = json.loads(string_msg)
        msg = Message(id=recieved_dict['id'], command=recieved_dict['command'])
        if recieved_dict.get('flags'):
            msg['flags'] = MsgFlag.fromDigit(recieved_dict.get('flags'))
        return msg
