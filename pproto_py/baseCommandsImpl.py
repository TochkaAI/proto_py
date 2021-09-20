import json

from . import config
from .baseCommands import BaseCommand, CLOSE_CONNECTION, PROTOCOL_COMPATIBLE, UNKNOWN, ERROR
from .message import Message


class Error(BaseCommand):
    COMMAND_UUID = ERROR.uuid


class CloseConnectionCommand(BaseCommand):
    COMMAND_UUID = CLOSE_CONNECTION.uuid

    @staticmethod
    def initial(conn, group, code, desc):
        msg = conn.create_command(CloseConnectionCommand)
        msg.set_content({'group': group, 'code': code, 'description': desc})
        return msg

    @staticmethod
    def answer(msg):
        if msg.my_connection.is_connected():
            msg.my_connection.close()
        return True

    @staticmethod
    def handler(msg):
        answer = msg.get_answer_copy()
        answer.set_content(None)
        answer.send_answer()
        answer.my_connection.close()


class ProtocolCompatibleCommand(BaseCommand):
    COMMAND_UUID = PROTOCOL_COMPATIBLE.uuid

    @staticmethod
    def initial(conn):
        msg = conn.create_command(ProtocolCompatibleCommand)
        msg.set_protocol_version_high(config.PROTOCOL_VERSION_LOW)
        msg.set_protocol_version_low(config.PROTOCOL_VERSION_HIGH)
        msg.set_max_time_life(5)
        return msg

    @staticmethod
    def answer(msg, group, code, descr):
        msg.my_connection.close()
        return True

    @staticmethod
    def handler(msg):
        connection = msg.my_connection

        def protocol_compatible(version_low, version_high):
            if version_high is None and version_low is None:
                return True
            if version_low > version_high:
                return False
            if version_high < config.PROTOCOL_VERSION_LOW:
                return False
            if version_low > config.PROTOCOL_VERSION_HIGH:
                return False
            return True
        if not config.CHECK_PROTOCOL_VERSION:
            return
        if not protocol_compatible(msg.get('PROTOCOL_VERSION_LOW'), msg.get('PROTOCOL_VERSION_HIGH')):
            message = f'Protocol versions incompatible. ' \
                      f'This protocol version: {config.PROTOCOL_VERSION_LOW}-{config.PROTOCOL_VERSION_HIGH}. ' \
                      f'Remote protocol version: {msg.get("PROTOCOL_VERSION_LOW")}-{msg.get("PROTOCOL_VERSION_HIGH")}'
            connection.exec_command_sync(CloseConnectionCommand, 0, 'afa4209c-bd5a-4791-9713-5c3f4ab3c52b', message)
            return False
        return True

    @staticmethod
    def timeout(msg):
        pass


class UnknownCommand(BaseCommand):
    COMMAND_UUID = UNKNOWN.uuid

    @staticmethod
    def initial(conn, unknown_answer):
        unkwonw_data = json.loads(unknown_answer)
        msg = conn.create_command(UnknownCommand)
        content = {
            'commandId': unkwonw_data['command'],
            'socketType': 2,
            'socketDescriptor': conn.fileno(),
            'socketName': str(conn.getpeername()),
            'addressProtocol': 'ip4',
            'address': conn.getpeername()[0],
            'addressScopeId': '',
            'port': conn.getpeername()[1]
        }
        msg.set_content(content)
        return msg

    @staticmethod
    def answer(*args, **kwargs):
        raise Exception('Если вы выдите этот эксепшн, значит что-то пошло не так')

    @staticmethod
    def handler(msg):
        connection = msg.my_connection
        unknown_command_uid = msg.get_content().get('commandId')
        connection.worker.unknown_command_list.append(unknown_command_uid)
        for req_msg in msg.my_connection.request_pool.values():
            if req_msg.get_command() == unknown_command_uid:
                fake_msg = Message(connection, id_=req_msg.get_id(), command_uuid=UNKNOWN)
                msg.my_connection.message_pool.add_message(fake_msg)
