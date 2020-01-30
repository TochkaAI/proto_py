from threading import Thread
import time

from strongTcpClient.message import Message
from strongTcpClient.userCommands import COMMAND_1, COMMAND_2


def command1(tcpCLient):
    # COMMAND_1 = "3c706211-f0c2-409f-af43-e1ed9951badb"
    def command1_answer():
        while True:
            if msg.getId() in tcpCLient.message_pool:
                tcpCLient.message_pool.dellMessage(msg)
                tcpCLient.request_pool.dellMessage(msg)
                break
            time.sleep(1)

    msg = Message.command(COMMAND_1)
    tcpCLient.send_message(msg)

    listener_thread = Thread(target=command1_answer)
    listener_thread.start()


def command2(tcpCLient):
    # COMMAND_2 = "589e873d-791a-40eb-9f95-695c92838e0b"
    def command2_answer():
        while True:
            if msg.getId() in tcpCLient.message_pool:
                tcpCLient.message_pool.dellMessage(msg)
                tcpCLient.request_pool.dellMessage(msg)
                break
            time.sleep(1)

    msg = Message.command(COMMAND_2)
    msg.setContent(dict(
        message="Test message",
        valueInt=10,
        valueDbl=1.256
    ))
    tcpCLient.send_message(msg)

    listener_thread = Thread(target=command2_answer)
    listener_thread.start()
