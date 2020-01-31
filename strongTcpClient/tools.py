import json
import datetime
from uuid import UUID, uuid4

from strongTcpClient.badSituations import NotImplementedCommand


def tryUuid(uuid):
    try:
        return str(UUID(str(uuid)))
    except ValueError as ex:
        return None


def getCommandByUUID(module, UUID):
    for cls in dir(module):
        obj = getattr(module, cls)
        if hasattr(obj, 'COMMAND_UUID') and getattr(obj, 'COMMAND_UUID') == UUID:
            return obj
    raise NotImplementedCommand(f'command {UUID} not implemented')


def getCommandStruct(module, moduleImpl):
    struct = {}
    for field in dir(module):
        if tryUuid(getattr(module, field)):
            uuid = getattr(module, field)
            struct[uuid] = (field, uuid, getCommandByUUID(moduleImpl, uuid))
    return struct


def dateTimeFromInt(intetime):
    return datetime.datetime.fromtimestamp(intetime / 1e3)


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
