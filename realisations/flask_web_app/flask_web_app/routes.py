from flask import render_template

from flask_web_app.remoteConn import CONNECTION
from flask_web_app import userCommandsImpl
from flask_web_app import app


@app.route('/')
def hello_world():
    context = {
        "conn_name": CONNECTION.getpeername(),
        "requests": CONNECTION.request_pool,
        "answer": CONNECTION.message_pool
    }
    return render_template('index.html', **context)
    # return f'Welcome to flask web app: we have connection: {CONNECTION.getpeername()}'


@app.route('/cmd1')
def cmd1():
    if CONNECTION:
        res = CONNECTION.exec_command_sync(userCommandsImpl.command1)
        return res.to_json()
    return 'No connection'


@app.route('/cmd2')
def cmd2():
    if CONNECTION:
        res = CONNECTION.exec_command_sync(userCommandsImpl.command2)
        return res.to_json()
    return 'No connection'


@app.route('/cmd3')
def cmd3():
    if CONNECTION:
        res = CONNECTION.exec_command_sync(userCommandsImpl.command3)
        return res.to_json()
    return 'No connection'

