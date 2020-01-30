from strongTcpClient.message import Message
from userCommands import COMMAND_1, COMMAND_2, COMMAND_3, \
    COMMAND_4, COMMAND_5, COMMAND_U, COMMAND_6, COMMAND_7
from strongTcpClient.baseCommands import BaseCommand
from strongTcpClient.tools import dateTimeFromInt


class command1(BaseCommand):
    @staticmethod
    def initial(client):
        msg = Message.command(client, COMMAND_1)
        return msg

    @staticmethod
    def answer(client, msg):
        print('COMMAND_1 anwser handler released')

    @staticmethod
    def handler(client, msg):
        anw = msg.getAnswerCopy()
        client.sennd_message()


class command2(BaseCommand):
    @staticmethod
    def initial(client):
        msg = Message.command(client, COMMAND_2)
        msg.setContent(dict(
            message="Test message",
            valueInt=10,
            valueDbl=1.256
        ))
        return msg

    @staticmethod
    def answer(client, msg):
        print('COMMAND_2 anwser handler released')


class command3(BaseCommand):
    @staticmethod
    def initial(client):
        msg = Message.command(client, COMMAND_3)
        return msg

    @staticmethod
    def answer(client, msg):
        print(f'COMMAND_3 anwser handler released with msg: {msg}')
        content = msg.getContent()
        if content:
            print(content.get('value1'))

class command4(BaseCommand):
    @staticmethod
    def initial(client):
        msg = Message.command(client, COMMAND_4)
        content = dict(
            id=123
        )
        msg.setContent(content)
        return msg

    @staticmethod
    def answer(client, msg):
        print(f'COMMAND_4 anwser handler released with msg: {msg}')


class command5(BaseCommand):
    @staticmethod
    def initial(client):
        msg = Message.command(client, COMMAND_5)
        return msg

    @staticmethod
    def answer(client, msg):
        print(f'COMMAND_5 anwser handler released with msg: {msg}')
        content = msg.getContent()
        if content:
            print(dateTimeFromInt(content.get('dtCurrent')))
            print(dateTimeFromInt(content.get('dtFixed')))


class commandU(BaseCommand):
    @staticmethod
    def initial(client):
        msg = Message.command(client, COMMAND_U)
        print(f'unknownMsgId: {msg.getId()}')
        return msg

    @staticmethod
    def answer(client, msg):
        print(f'COMMAND_U anwser handler released with msg: {msg}')


class command6(BaseCommand):
    @staticmethod
    def initial(client):
        msg = Message.command(client, COMMAND_6)
        msg.setTag(10, 0)
        msg.setTag(56, 5)
        msg.setTag(25, 108)
        return msg

    @staticmethod
    def answer(client, msg):
        print('COMMAND_6 anwser handler released')


class command7(BaseCommand):
    @staticmethod
    def initial(client, timelife):
        msg = Message.command(client, COMMAND_7)
        msg.setMaxTimeLife(timelife)
        return msg

    @staticmethod
    def answer(client, msg):
        print('COMMAND_7 anwser handler released')

    @staticmethod
    def timeout():
        print('Ваще, пох, не дождались команду 7')
