import socket
import uuid
from threading import Thread
import time

from strongTcpClient import config
from strongTcpClient import baseCommands
from strongTcpClient.message import Message
from strongTcpClient.messagePool import MessagePool
from strongTcpClient.baseCommandsImpl import CloseConnectionCommand
from strongTcpClient.tools import getCommandNameList, tryUuid


class StrongClient:
    def __init__(self, client_commands=[]):
        self.ip = config.ip
        self.port = config.port

        self.isRunning = False

        self.sock = socket.socket()
        self.listener_thread = Thread(target=self.main_listener)
        self.message_pool = MessagePool()
        self.request_pool = MessagePool()

        self.base_commands_list = getCommandNameList(baseCommands)
        self.user_commands_list = client_commands

        self.unknown_command_list = []

    def getCommandName(self, commandUuid):
        commands_list = self.base_commands_list + self.user_commands_list
        for comm_name in commands_list:
            value = comm_name[1]
            if tryUuid(value) and value == commandUuid:
                return comm_name[0]
        return None

    def send(self, bdata):
        self.sock.send(bdata)

    def msend(self, bdata):
        bdata_len = (len(bdata)).to_bytes(4, 'big')
        self.sock.send(bdata_len + bdata)

    def recv(self, buffsize, timeout=None):
        self.sock.settimeout(timeout)
        try:
            answer = self.sock.recv(buffsize)
            return answer
        except socket.timeout as timeex:
            raise TimeoutError('Удалённый сервер не ответил на приветствие в установленное время')
        finally:
            self.sock.settimeout(None)

    def mrecv(self):
        banswer_size = self.recv(4)
        answer_size = int.from_bytes(banswer_size, 'big')
        ball_answer = self.recv(answer_size)
        return ball_answer.decode()

    def send_message(self, message, need_answer=True):
        if message.getCommand() in self.unknown_command_list:
            # TODO: наверное стоит сделать своё исключение на это дело
            raise Exception('Попытка оптравки неизвестной команды!')
        self.msend(message.getBytes())
        print(f'Msg JSON send: {message.getBytes().decode()}')
        if need_answer:
            self.request_pool.addMessage(message)

    def send_hello(self):
        bdata = uuid.UUID(baseCommands.JSON_PROTOCOL_FORMAT).bytes
        self.send(bdata)
        answer = self.recv(16, timeout=3)
        if answer != bdata:
            raise TypeError('Удалённый сервер не согласовал тип протокола')

    def protocol_compatible_req(self):
        msg = Message.command(self, baseCommands.PROTOCOL_COMPATIBLE)
        msg['protocolVersionLow'] = config.protocolVersionLow
        msg['protocolVersionHigh'] = config.protocolVersionHigh
        self.send_message(msg, need_answer=False)

    def protocol_compatible_handler(self, msg):
        def protocol_compatible(versionLow, versionHigh):
            if versionHigh is None and versionLow is None:
                # Видимо ничего не надо делать
                return True
            if versionLow > versionHigh:
                return False
            if versionHigh < config.protocolVersionLow:
                return False
            if versionLow > config.protocolVersionHigh:
                return False
            return True
        if not config.checkProtocolVersion:
            return
        if not protocol_compatible(msg.get('protocolVersionLow'), msg.get('protocolVersionHigh')):
            msg = f'Protocol versions incompatible. This protocol version: {config.protocolVersionLow}-{config.protocolVersionHigh}. ' \
                  f'Remote protocol version: {msg.get("protocolVersionLow")}-{msg.get("protocolVersionHigh")}'
            self.finish(code=0, description=msg, is_async=True)
            # raise ProtocolIncompatibleEx(msg)

    def close_connection_handler(self, msg):
        self.send_message(msg.getAnswerCopy(), need_answer=False)
        self.isRunning = False

    def unknow_command_handler(self, msg):
        unknown_command_uid = msg.getContent().get('commandId')
        self.unknown_command_list.append(unknown_command_uid)
        for req_msg in self.request_pool.values():
            if req_msg.getCommand() == unknown_command_uid:
                msg = Message(self, id=req_msg.getId(), command=baseCommands.UNKNOWN)
                self.message_pool.addMessage(msg)

    def exec_command_sync(self, command, *args, **kwargs):
        msg = command.initial(self, *args, **kwargs)
        self.send_message(msg)

        max_time_life = msg.getMaxTimeLife()
        t_end = None
        if max_time_life:
            t_end = time.time() + max_time_life
        while True and self.isRunning:
            if t_end and time.time() > t_end:
                self.request_pool.dellMessage(msg)
                return command.timeout()

            if msg.getId() in self.message_pool:
                ans_msg = self.message_pool[msg.getId()]
                self.request_pool.dellMessage(msg)
                self.message_pool.dellMessage(ans_msg)

                if ans_msg.getCommand() == baseCommands.UNKNOWN:
                    return command.unknown(msg)

                return command.answer(self, ans_msg, *args, **kwargs)

            time.sleep(1)

    def exec_command_async(self, command, *args, **kwargs):
        def answer_handler():
            max_time_life = msg.getMaxTimeLife()
            t_end = None
            if max_time_life:
                t_end = time.time() + max_time_life
            while True and self.isRunning:
                if t_end and time.time() > t_end:
                    self.request_pool.dellMessage(msg)
                    command.timeout()
                    return

                if msg.getId() in self.message_pool:
                    ans_msg = self.message_pool[msg.getId()]
                    self.request_pool.dellMessage(msg)
                    self.message_pool.dellMessage(ans_msg)

                    if ans_msg.getCommand() == baseCommands.UNKNOWN:
                        command.unknown(msg)
                        return

                    command.answer(self, ans_msg, *args, **kwargs)
                    return
                time.sleep(1)

        msg = command.initial(self, *args, **kwargs)
        self.send_message(msg)

        listener_thread = Thread(target=answer_handler)
        listener_thread.start()

    def base_commands_handlers(self, msg):
        # Это команда с той стороны, её нужно прям тут и обработать!
        if msg.getCommand() == baseCommands.PROTOCOL_COMPATIBLE:
            self.protocol_compatible_handler(msg)
        elif msg.getCommand() == baseCommands.UNKNOWN:
            self.unknow_command_handler(msg)
        elif msg.getCommand() == baseCommands.CLOSE_CONNECTION:
            self.close_connection_handler(msg)

    def user_commands_handlers(self, msg):
        pass

    def main_listener(self):
        while self.isRunning:
            answer = self.mrecv()
            if answer:
                print(f'Msg JSON receeved: {answer}')
                msg = Message.fromString(self, answer)
                print(f'Msg received: {msg}')
                if msg.getId() not in self.request_pool:
                    # Это команды
                    if msg.getCommand() in [uuid[1] for uuid in self.base_commands_list]:
                        self.base_commands_handlers(msg)
                    else:
                        self.user_commands_handlers(msg)
                else:
                    # Это ответы, который нужно обработать
                    self.message_pool.addMessage(msg)

        print(f'Disconect from host: {self.ip}:{self.port}')

    def start(self):
        ''' Порядок установки соединения '''
        try:
            self.sock.connect((self.ip, self.port))
        except ConnectionRefusedError as ex:
            print('Не удалось, установить соединение, удалённый сервер не доступен')
            return
        ''' После установки TCP соединения клиент отправляет на сокет сервера 16 байт (обычный uuid). 
            Это сигнатура протокола. Строковое представление сигнатуры для json формата: "fea6b958-dafb-4f5c-b620-fe0aafbd47e2". 
            Если сервер присылает назад этот же uuid, то все ОК - можно работать'''
        self.send_hello()
        ''' После того как сигнатуры протокола проверены клиент и сервер отправляют друг другу первое сообщение - 
            ProtocolCompatible.'''
        self.protocol_compatible_req()

        self.isRunning = True
        self.listener_thread.start()

    def finish(self, code, description, is_async=False):
        if not self.isRunning:
            return

        if is_async:
            self.exec_command_async(CloseConnectionCommand, code, description)
        else:
            self.exec_command_sync(CloseConnectionCommand, code, description)
