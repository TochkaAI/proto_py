import userCommandsImpl, userCommands
from strongTcpClient import TcpServer
from strongTcpClient import TcpSocket
from userCommandsImpl import (
    # command1,
    command2,
    command3, command4, command5, commandU, command6, command7)


def like_client():
    # Этот клиент будет подключаться
    ip_to_connect = '127.0.0.1'
    port_to_connect = 48062
    tcp_worker = TcpSocket(ip_to_connect, port_to_connect, userCommands, userCommandsImpl)
    connection = tcp_worker.connect()

    try:
        while True:
            value = input("INPUT: ")
            if value == 'exit':
                break
            elif value == 'cmd1':
                connection.exec_command_async(command1)
            elif value == 'cmd2':
                connection.exec_command_sync(command2)
            elif value == 'cmd3':
                connection.exec_command_async(command3)
            elif value == 'cmd4':
                connection.exec_command_async(command4)
            elif value == 'cmd5':
                connection.exec_command_async(command5)
            elif value == 'cmdu':
                connection.exec_command_async(commandU)
            elif value == 'cmd6':
                connection.exec_command_async(command6)
            elif value == 'c7':
                connection.exec_command_sync(command7, 5)

            elif value == 'info':
                print(tcp_worker.connection_pool.info())
                print(tcp_worker.user_commands_list)

            else:
                print('Unkwon command, pls reenter')
    finally:
        tcp_worker.disconnect()

def like_server():
    connection = None
    def client_add_handler(conn):
        nonlocal connection
        connection = conn

    def client_dis_handler(conn):
        nonlocal connection
        if conn == connection:
            connection = None

    # А этот клиент будет слушать, и принимать входящие подключения
    listen_ip = '127.0.0.1'
    listen_port = 48063
    listening_worker = TcpServer(listen_ip, listen_port, userCommands, userCommandsImpl)
    listening_worker.run(client_add_handler, client_dis_handler)

    try:
        while True:
            value = input("INPUT: ")
            if value == 'exit':
                break
            elif value == 'info':
                print(listening_worker.connection_pool.info())
                print(listening_worker.user_commands_list)
            elif value == 'cmd1':
                if connection:
                    connection.exec_command_sync(command1)
                else:
                    print('некому отправлять!')

            else:
                print('Unkwon command, pls reenter')

    finally:
        listening_worker.stop()

if __name__ == '__main__':
    # like_client()
    like_server()

    print('finish')
