'''
Список констант с существующими базовыми командами
'''
import sys

Command1 = "COMMAND_1"
Command2 = "COMMAND_2"
Command3 = "COMMAND_3"
Command4 = "COMMAND_4"
Command5 = "COMMAND_5"
Command6 = "COMMAND_6"
Command7 = "COMMAND_7"

CommandU = "COMMAND_U"


def REGISTRY_COMMAND_SINGLPROC(name, uuid):
    setattr(sys.modules[__name__], name, uuid)


REGISTRY_COMMAND_SINGLPROC(Command1,                "3c706211-f0c2-409f-af43-e1ed9951badb")
REGISTRY_COMMAND_SINGLPROC(Command2,                "589e873d-791a-40eb-9f95-695c92838e0b")
REGISTRY_COMMAND_SINGLPROC(Command3,                "162fc76d-6c3e-4b19-afb0-e655dbed83a6")
REGISTRY_COMMAND_SINGLPROC(Command4,                "9928db8e-d374-4eb9-8f43-d2d85af8a6b6")
REGISTRY_COMMAND_SINGLPROC(Command5,                "07386a14-f2cd-408d-bf58-48b7175d0f46")
REGISTRY_COMMAND_SINGLPROC(Command6,                "11c8baa3-53c2-4264-ad31-24f5b7c39b4b")
REGISTRY_COMMAND_SINGLPROC(Command7,                "c5d3c726-1fcb-420f-8428-0907e5ec8408")

REGISTRY_COMMAND_SINGLPROC(CommandU,                "df0b276d-771f-458b-bd4a-c8e12739dafb")
