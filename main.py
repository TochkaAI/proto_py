from strongTcpClient.сlient import StrongClient
from strongTcpClient.userCommandsImpl import command1, command2, command3, command4, command5, commandU

if __name__ == '__main__':
    client = StrongClient()
    client.start()

    try:
        while True:
            value = input("Enter command: \n\r")
            if value == 'exit':
                break
            elif value == 'cmd1':
                client.exec_command_async(command1)
            elif value == 'cmd2':
                client.exec_command_sync(command2)
            elif value == 'cmd3':
                client.exec_command_async(command3)
            elif value == 'cmd4':
                client.exec_command_async(command4)
            elif value == 'cmd5':
                client.exec_command_async(command5)
            elif value == 'cmdu':
                client.exec_command_async(commandU)

            elif value == 'info':
                print('\n\r'.join(client.request_pool))
                print('\n\r'.join(client.message_pool))
    finally:
        client.finish()

    print('finish')
