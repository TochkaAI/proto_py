from packages.strongTcpClient import Message
from packages.strongTcpClient import BaseCommand
from .userCommands import (
        COMMAND_1,
        COMMAND_2,
        COMMAND_3,
        COMMAND_4,
        COMMAND_5,
        COMMAND_U,
        COMMAND_6,
        COMMAND_7
    )


class command1(BaseCommand):
    COMMAND_UUID = COMMAND_1
    @staticmethod
    def initial(connection):
        msg = connection.create_command_msg(COMMAND_1)
        return msg

    @staticmethod
    def answer(msg):
        return msg

    @staticmethod
    def handler(msg):
        print('COMMAND_1 handler released')
        ans = msg.get_answer_copy()
        ans.send_message()
        print('SEND ANSWER BACK')


class command2(BaseCommand):
    COMMAND_UUID = COMMAND_2
    @staticmethod
    def initial(connection):
        msg = Message.command(connection, COMMAND_2)
        msg.set_content(dict(
            message="Test message",
            valueInt=10,
            valueDbl=1.256
        ))
        return msg

    @staticmethod
    def answer(msg):
        return msg

    @staticmethod
    def handler(msg):
        ans = msg.get_answer_copy()
        content = ans.get_content()
        content['message'] = 'GO BACK SOME TEXT'
        ans.set_content(content)
        ans.send_message()


class command3(BaseCommand):
    COMMAND_UUID = COMMAND_3
    @staticmethod
    def initial(connection, content):
        msg = Message.command(connection, COMMAND_3)
        msg.set_content(content)
        return msg

    @staticmethod
    def answer(msg):
        return msg

    @staticmethod
    def handler(msg):
        print(f'COMMAND 3 HANDREL RELEASED')
        print(f'msg {msg} was recieved')


class command4(BaseCommand):
    COMMAND_UUID = COMMAND_4
    @staticmethod
    def initial(connection):
        msg = Message.command(connection, COMMAND_4)
        content = dict(
            id=123
        )
        msg.set_content(content)
        return msg

    @staticmethod
    def answer(msg):
        return msg


class command5(BaseCommand):
    COMMAND_UUID = COMMAND_5
    @staticmethod
    def initial(connection):
        msg = Message.command(connection, COMMAND_5)
        return msg

    @staticmethod
    def answer(msg):
        return msg


class commandU(BaseCommand):
    COMMAND_UUID = COMMAND_U
    @staticmethod
    def initial(connection):
        msg = Message.command(connection, COMMAND_U)
        print(f'unknownMsgId: {msg.get_id()}')
        return msg

    @staticmethod
    def answer(msg):
        print(f'COMMAND_U anwser handler released with msg: {msg}')


class command6(BaseCommand):
    COMMAND_UUID = COMMAND_6
    @staticmethod
    def initial(connection):
        msg = Message.command(connection, COMMAND_6)
        msg.set_tag(10, 0)
        msg.set_tag(56, 5)
        msg.set_tag(25, 108)
        return msg

    @staticmethod
    def answer(msg):
        return msg


class command7(BaseCommand):
    COMMAND_UUID = COMMAND_7
    @staticmethod
    def initial(connection, timelife):
        msg = Message.command(connection, COMMAND_7)
        msg.set_max_time_life(timelife)
        return msg

    @staticmethod
    def answer(msg):
        return msg

    @staticmethod
    def timeout():
        print('Ваще, пох, не дождались команду 7')
