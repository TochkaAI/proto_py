import json

from flask import Flask

import userCommands
import userCommandsImpl
from packages.strongTcpClient.tcpSocket import TcpSocket

app = Flask(__name__)
app.debug = True
connection = None


@app.route('/')
def hello_world():
    if connection:
        res = connection.exec_command_sync(userCommandsImpl.command2)
        return json.dumps(dict(result=res.to_json()))
    return 'No connection'


@app.route('/cmd3')
def cmd3():
    if connection:
        res = connection.exec_command_sync(userCommandsImpl.command3)
        return res.to_json()
    return 'No connection'


if __name__ == '__main__':
    ip_to_connect = '127.0.0.1'
    port_to_connect = 48062
    tcp_worker = TcpSocket(ip_to_connect, port_to_connect, userCommands, userCommandsImpl)
    connection = tcp_worker.connect()
    app.run()
