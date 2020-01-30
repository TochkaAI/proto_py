from strongTcpClient.сlient import StrongClient
from strongTcpClient.tools import getCommandNameList
from userCommandsImpl import command1, command2, command3, command4, command5, commandU, command6, command7
import userCommands

def like_client():
    # Этот клиент будет подключаться
    ip_to_connect = '127.0.0.1'
    port_to_connect = 48062
    connect_client = StrongClient(ip_to_connect, port_to_connect, getCommandNameList(userCommands))
    connection = connect_client.connect()

    try:
        while True:
            value = input("")
            if value == 'exit':
                break
            elif value == 'cmd1':
                connect_client.exec_command_async(command1, connection)
            elif value == 'cmd2':
                connect_client.exec_command_sync(command2, connection)
            elif value == 'cmd3':
                connect_client.exec_command_async(command3, connection)
            elif value == 'cmd4':
                connect_client.exec_command_async(command4, connection)
            elif value == 'cmd5':
                connect_client.exec_command_async(command5, connection)
            elif value == 'cmdu':
                connect_client.exec_command_async(commandU, connection)
            elif value == 'cmd6':
                connect_client.exec_command_async(command6, connection)
            elif value == 'c7':
                connect_client.exec_command_sync(command7, connection, 5)

            elif value == 'info':
                print(connect_client.connection_pool.info())

            else:
                print('Unkwon command, pls reenter')
    finally:
        connect_client.finish_all(1, 'Bye-Bye!')

def like_server():
    connection = None
    def client_add_handler(conn):
        nonlocal connection
        connection = conn

    # А этот клиент будет слушать, и принимать входящие подключения
    listen_ip = '127.0.0.1'
    listen_port = 48063
    listen_client = StrongClient(listen_ip, listen_port, getCommandNameList(userCommands))
    listen_client.listen(client_add_handler)

    try:
        while True:
            value = input("")
            if value == 'exit':
                break
            elif value == 'info':
                print(listen_client.connection_pool.info())
            elif value == 'cmd1':
                if connection:
                    listen_client.exec_command_async(command1, connection)
                else:
                    print('некому отправлять!')

            else:
                print('Unkwon command, pls reenter')

    finally:
        listen_client.finish_all(1, 'Bye-Bye!')
        pass

if __name__ == '__main__':
    like_client()
    # like_server()

    print('finish')
