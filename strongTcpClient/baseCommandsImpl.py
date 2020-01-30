from strongTcpClient.baseCommands import BaseCommand, CLOSE_CONNECTION
from strongTcpClient.message import Message


class CloseConnectionCommand(BaseCommand):
    @staticmethod
    def initial(client, code, desc):
        msg = Message.command(client, CLOSE_CONNECTION)
        content = dict(
            code=code,
            description=desc
        )
        msg.setContent(content)
        return msg

    @staticmethod
    def answer(client, msg, code, descr):
        client.isRunning = False
        client.sock.close()
