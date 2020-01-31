from strongTcpClient.message import Message
from userCommands import COMMAND_1, COMMAND_2, COMMAND_3, \
    COMMAND_4, COMMAND_5, COMMAND_U, COMMAND_6, COMMAND_7
from strongTcpClient.baseCommands import BaseCommand
from strongTcpClient.tools import dateTimeFromInt


class command1(BaseCommand):
    COMMAND_UUID = COMMAND_1
    @staticmethod
    def initial(client):
        msg = Message.command(client, COMMAND_1)
        return msg

    @staticmethod
    def answer(client, msg):
        print('COMMAND_1 anwser handler released')

    @staticmethod
    def handler(client, msg):
        print('COMMAND_1 handler released')
        ans = msg.getAnswerCopy()
        msg.my_connection.send_message(ans)
        print('SEND ANSWER BACK')


class command2(BaseCommand):
    COMMAND_UUID = COMMAND_2
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

    @staticmethod
    def handler(client, msg):
        ans = msg.getAnswerCopy()
        content = ans.getContent()
        content['message'] = 'GO BACK SOME TEXT'
        ans.setContent(content)
        msg.my_connection.send_message(ans)


class command3(BaseCommand):
    COMMAND_UUID = COMMAND_3
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

    @staticmethod
    def handler(client, msg):
        print(f'COMMAND 3 HANDREL RELEASED')
        print(f'msg {msg} was recieved')


class command4(BaseCommand):
    COMMAND_UUID = COMMAND_4
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
    COMMAND_UUID = COMMAND_5
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
    COMMAND_UUID = COMMAND_U
    @staticmethod
    def initial(client):
        msg = Message.command(client, COMMAND_U)
        print(f'unknownMsgId: {msg.getId()}')
        return msg

    @staticmethod
    def answer(client, msg):
        print(f'COMMAND_U anwser handler released with msg: {msg}')


class command6(BaseCommand):
    COMMAND_UUID = COMMAND_6
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
    COMMAND_UUID = COMMAND_7
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
