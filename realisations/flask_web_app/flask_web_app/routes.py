from flask import render_template, request, jsonify
from flask import Blueprint

from remoteConn import CONNECTION
import userCommandsImpl


routes = Blueprint('routes', __name__)


def get_context():
    if CONNECTION:
        return {
            "conn_name": CONNECTION.getpeername(),
            "requests": CONNECTION.request_pool,
            "answer": CONNECTION.message_pool
        }
    else:
        return {}

@routes.route('/')
def hello_world():
    return render_template('index.html', **get_context())
    # return f'Welcome to flask web app: we have connection: {CONNECTION.getpeername()}'


@routes.route('/cmd1', methods=['GET', 'POST'])
def cmd1():
    if request.method == 'GET':
        return render_template('cmd1.html', **get_context())
    if request.method == 'POST':
        if CONNECTION:
            res = CONNECTION.exec_command_sync(userCommandsImpl.command1).to_serializable_dict()
            return jsonify(res)
    raise Exception('no connection')


@routes.route('/cmd2')
def cmd2():
    if CONNECTION:
        res = CONNECTION.exec_command_sync(userCommandsImpl.command2)
        return res.to_json()
    return 'No connection'


@routes.route('/cmd3', methods=['GET', 'POST'])
def cmd3():
    if request.method == 'GET':
        return render_template('cmd3.html', **get_context())
    if request.method == 'POST':
        if CONNECTION:
            content = dict(
                value1=request.form.get('value1', ''),
                value2=int(request.form.get('value2') if request.form.get('value2') else 0),
                value3=float(request.form.get('value3') if request.form.get('value3') else 0),
                value4=int(request.form.get('value4') if request.form.get('value4') else 0)
            )
            res = CONNECTION.exec_command_sync(userCommandsImpl.command3, content)
            res = res.get_content()
            return jsonify(res)
    raise Exception('no connection')

