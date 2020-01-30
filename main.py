from strongTcpClient.сlient import StrongClient
from strongTcpClient.tools import getCommandNameList
from userCommandsImpl import command1, command2, command3, command4, command5, commandU, command6, command7
import userCommands

if __name__ == '__main__':
    client = StrongClient(getCommandNameList(userCommands))
    client.start()

    try:
        while True and client.isRunning:
            value = input("")
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
            elif value == 'cmd6':
                client.exec_command_async(command6)
            elif value == 'c7':
                client.exec_command_sync(command7, 5)

            elif value == 'info':
                print('\n\r'.join(client.request_pool))
                print('\n\r'.join(client.message_pool))

            else:
                print('Unkwon command, pls reenter')
    finally:
        client.finish(1, 'Bye-Bye!')

    print('finish')
