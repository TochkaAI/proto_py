import json
import datetime
from uuid import UUID, uuid4


def tryUuid(uuid):
    try:
        return str(UUID(str(uuid)))
    except ValueError as ex:
        return None


def getCommandNameList(module):
    return [(comm, getattr(module, comm)) for comm in dir(module) if '__' not in comm]


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
