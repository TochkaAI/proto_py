'''
Список констант с существующими базовыми командами
'''
import sys

Command1 = "COMMAND_1"
Command2 = "COMMAND_2"


def REGISTRY_COMMAND_SINGLPROC(name, uuid):
    setattr(sys.modules[__name__], name, uuid)


REGISTRY_COMMAND_SINGLPROC(Command1,                "3c706211-f0c2-409f-af43-e1ed9951badb")
REGISTRY_COMMAND_SINGLPROC(Command2,                "589e873d-791a-40eb-9f95-695c92838e0b")