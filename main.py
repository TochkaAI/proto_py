from strongTcpClient.сlient import StrongClient
from strongTcpClient.userCommandsImpl import command1, command2

if __name__ == '__main__':
    client = StrongClient()
    client.start()

    while True:
        value = input("Enter command: \n\r")
        if value == 'exit':
            break
        elif value == 'cmd1':
            client.exec_command(command1)
        elif value == 'cmd2':
            client.exec_command(command2)
        elif value == 'info':
            print(client.request_pool)
            print(client.message_pool)

    client.finish()
    print('finish')
