import socket
import time
from threading import Thread

from strongTcpClient import baseCommands
from strongTcpClient.messagePool import MessagePool
from strongTcpClient.logger import write_info
from strongTcpClient.badSituations import UnknownCommandSend


class Connection:
    def __init__(self, worker, socket_=None):
        self.message_pool = MessagePool()
        self.request_pool = MessagePool()

        self.worker = worker

        if socket_ is None:
            socket_ = socket.socket()

        self.socket = socket_

    def setSocket(self, socket_):
        self.socket = socket_

    def getpeername(self):
        return self.socket.getpeername()

    def send(self, bdata):
        return self.socket.send(bdata)

    def connect(self, *args, **kwargs):
        return self.socket.connect(*args, **kwargs)

    def close(self):
        return self.socket.close()

    def msend(self, bdata):
        bdata_len = (len(bdata)).to_bytes(4, 'big')
        self.socket.send(bdata_len + bdata)

    def recv(self, buffsize, timeout=None):
        self.socket.settimeout(timeout)
        try:
            answer = self.socket.recv(buffsize)
            return answer
        except socket.timeout:
            raise TimeoutError('Удалённый сервер не ответил на приветствие в установленное время')
        finally:
            self.socket.settimeout(None)

    def mrecv(self):
        banswer_size = self.socket.recv(4)
        answer_size = int.from_bytes(banswer_size, 'big')
        ball_answer = self.socket.recv(answer_size)
        return ball_answer.decode()

    def fileno(self):
        return self.socket.fileno()

    def send_message(self, message, need_answer=False):
        if message.getCommand() in self.worker.unknown_command_list:
            # TODO: наверное стоит сделать своё исключение на это дело
            raise UnknownCommandSend('Попытка оптравки неизвестной команды!')

        message.setConnection(self)
        self.msend(message.getBytes())
        write_info(f'[{self.getpeername()}] Msg JSON send: {message.getBytes().decode()}')
        if need_answer:
            self.request_pool.addMessage(message)



    def exec_cmmand(self, command, *args, **kwargs):
        msg = command.initial(self.worker, *args, **kwargs)
        self.worker.send_message(msg, self)

    def exec_command_sync(self, command, *args, **kwargs):
        msg = command.initial(self.worker, *args, **kwargs)
        self.send_message(msg, need_answer=True)

        max_time_life = msg.getMaxTimeLife()
        t_end = None
        if max_time_life:
            t_end = time.time() + max_time_life
        while True:
            if t_end and time.time() > t_end:
                self.request_pool.dellMessage(msg)
                return command.timeout()

            if msg.getId() in self.message_pool:
                ans_msg = self.message_pool[msg.getId()]
                self.request_pool.dellMessage(msg)
                self.message_pool.dellMessage(ans_msg)

                if ans_msg.getCommand() == baseCommands.UNKNOWN:
                    return command.unknown(msg)

                return command.answer(self.worker, ans_msg, *args, **kwargs)

            time.sleep(1)

    def exec_command_async(self, command, *args, **kwargs):
        def answer_handler():
            max_time_life = msg.getMaxTimeLife()
            t_end = None
            if max_time_life:
                t_end = time.time() + max_time_life
            while True:
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

                    command.answer(self.worker, ans_msg, *args, **kwargs)
                    return
                time.sleep(1)

        msg = command.initial(self.worker, *args, **kwargs)
        self.send_message(msg, need_answer=True)

        listener_thread = Thread(target=answer_handler)
        listener_thread.daemon = True
        listener_thread.start()
