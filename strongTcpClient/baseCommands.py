'''
Список констант с существующими базовыми командами
'''
import sys

JSON_PROTOCOL_FORMAT = 'fea6b958-dafb-4f5c-b620-fe0aafbd47e2'

Unknown = "UNKNOWN"
Error = "ERROR"
ProtocolCompatible = "PROTOCOL_COMPATIBLE"
CloseConnection = "CLOSE_CONNECTION"

def REGISTRY_COMMAND(name, uuid):
    setattr(sys.modules[__name__], name, uuid)


REGISTRY_COMMAND(Unknown,            "4aef29d6-5b1a-4323-8655-ef0d4f1bb79d")
REGISTRY_COMMAND(Error,              "b18b98cc-b026-4bfe-8e33-e7afebfbe78b")
REGISTRY_COMMAND(ProtocolCompatible, "173cbbeb-1d81-4e01-bf3c-5d06f9c878c3")
REGISTRY_COMMAND(CloseConnection,    "e71921fd-e5b3-4f9b-8be7-283e8bb2a531")
