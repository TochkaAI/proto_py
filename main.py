from strongTcpClient.сlient import StrongClient

if __name__ == '__main__':
    client = StrongClient()
    client.start()

    value = input("Press enter to finish")
    client.finish()
    print('finish')
