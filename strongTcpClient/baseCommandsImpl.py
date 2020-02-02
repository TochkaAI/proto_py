from strongTcpClient import config
from strongTcpClient.baseCommands import BaseCommand, CLOSE_CONNECTION, PROTOCOL_COMPATIBLE, UNKNOWN, ERROR
from strongTcpClient.message import Message


class Error(BaseCommand):
    COMMAND_UUID = ERROR


class CloseConnectionCommand(BaseCommand):
    COMMAND_UUID = CLOSE_CONNECTION

    @staticmethod
    def initial(conn, code, desc):
        msg = Message.command(conn, CLOSE_CONNECTION)
        content = dict(
            code=code,
            description=desc
        )
        msg.set_content(content)
        return msg

    @staticmethod
    def answer(conn, msg, code, descr):
        conn.close()
        return True

    @staticmethod
    def handler(conn, msg):
        answer = msg.get_answer_copy()
        answer.set_content(None)
        conn.send_message(answer)
        conn.close()


class ProtocolCompatibleCommand(BaseCommand):
    COMMAND_UUID = PROTOCOL_COMPATIBLE

    @staticmethod
    def initial(conn):
        msg = conn.create_command_msg(conn, PROTOCOL_COMPATIBLE)
        msg.set_protocol_version_high(config.protocolVersionLow)
        msg.set_protocol_version_low(config.protocolVersionHigh)
        return msg

    @staticmethod
    def answer(client, msg, code, descr):
        msg.my_connection.close()
        return True

    @staticmethod
    def handler(client, msg):
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
            message = f'Protocol versions incompatible. This protocol version: {config.protocolVersionLow}-{config.protocolVersionHigh}. ' \
                  f'Remote protocol version: {msg.get("protocolVersionLow")}-{msg.get("protocolVersionHigh")}'
            client.exec_command_sync(CloseConnectionCommand, msg.my_connection, 0, message)
            return False
        return True


class UnknownCommand(BaseCommand):
    COMMAND_UUID = UNKNOWN

    @staticmethod
    def initial(*args, **kwargs):
        pass

    @staticmethod
    def answer(*args, **kwargs):
        pass

    @staticmethod
    def handler(client, msg):
        unknown_command_uid = msg.get_content().get('commandId')
        client.unknown_command_list.append(unknown_command_uid)
        for req_msg in msg.my_connection.request_pool.values():
            if req_msg.get_command() == unknown_command_uid:
                fake_msg = Message(client, id=req_msg.get_id(), command=UNKNOWN)
                msg.my_connection.message_pool.add_message(fake_msg)