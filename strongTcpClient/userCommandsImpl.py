from strongTcpClient.message import Message
from strongTcpClient.userCommands import COMMAND_1, COMMAND_2, COMMAND_3, \
    COMMAND_4, COMMAND_5, COMMAND_6, COMMAND_7, COMMAND_U
from strongTcpClient.baseUserCommand import BaseUserCommand
from strongTcpClient.tools import dateTimeFromInt


class command1(BaseUserCommand):
    @staticmethod
    def initial():
        msg = Message.command(COMMAND_1)
        return msg

    @staticmethod
    def answer(msg):
        print('COMMAND_1 anwser handler released')


class command2(BaseUserCommand):
    @staticmethod
    def initial():
        msg = Message.command(COMMAND_2)
        msg.setContent(dict(
            message="Test message",
            valueInt=10,
            valueDbl=1.256
        ))
        return msg

    @staticmethod
    def answer(msg):
        print('COMMAND_2 anwser handler released')


class command3(BaseUserCommand):
    @staticmethod
    def initial():
        msg = Message.command(COMMAND_3)
        return msg

    @staticmethod
    def answer(msg):
        print(f'COMMAND_3 anwser handler released with msg: {msg}')
        content = msg.getContent()
        if content:
            print(content.get('value1'))

class command4(BaseUserCommand):
    @staticmethod
    def initial():
        msg = Message.command(COMMAND_4)
        content = dict(
            id=123
        )
        msg.setContent(content)
        return msg

    @staticmethod
    def answer(msg):
        print(f'COMMAND_4 anwser handler released with msg: {msg}')


class command5(BaseUserCommand):
    @staticmethod
    def initial():
        msg = Message.command(COMMAND_5)
        return msg

    @staticmethod
    def answer(msg):
        print(f'COMMAND_5 anwser handler released with msg: {msg}')
        content = msg.getContent()
        if content:
            print(dateTimeFromInt(content.get('dtCurrent')))
            print(dateTimeFromInt(content.get('dtFixed')))

class commandU(BaseUserCommand):
    @staticmethod
    def initial():
        msg = Message.command(COMMAND_U)
        print(f'unknownMsgId: {msg.getId()}')
        return msg

    @staticmethod
    def answer(msg):
        print(f'COMMAND_U anwser handler released with msg: {msg}')
