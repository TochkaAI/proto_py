import json
from uuid import UUID, uuid4

from strongTcpClient import baseCommands
from strongTcpClient import userCommands


def tryUuid(uuid):
    try:
        return str(UUID(str(uuid)))
    except ValueError as ex:
        return None


def getCommandName(commandUuid):
    base_commands_list = [comm for comm in dir(baseCommands) if '__' not in comm]
    for comm_name in base_commands_list:
        value = getattr(baseCommands, comm_name)
        if tryUuid(value) and value == commandUuid:
            return comm_name
    user_commands_list = [comm for comm in dir(userCommands) if '__' not in comm]
    for comm_name in user_commands_list:
        value = getattr(userCommands, comm_name)
        if tryUuid(value) and value == commandUuid:
            return comm_name
    return 'UNKNOWN'


class Data(dict):
    def __init__(self, command):
        self['id'] = str(uuid4())
        self['command'] = command

    def addContent(self, content):
        if content is not None:
            self['content'] = content


    def addFlags(self, bflags):
        if bflags is not None:
            self['flags'] = bflags

    def json(self):
        return json.dumps(self)
