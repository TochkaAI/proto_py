from flask import render_template, request, jsonify
from flask import Blueprint
from flask_login import current_user

from .remoteConn import CONNECTION
from . import userCommandsImpl


routes = Blueprint('routes', __name__)


def get_context():
    conn = CONNECTION.get_connection()
    if conn:
        return {
            "connect_is_connected": conn.is_connected(),
            "conn_name": conn.getpeername(),
            "requests": conn.request_pool,
            "answer": conn.message_pool,
            "user_name": current_user.name if current_user.is_authenticated else ''
        }
    else:
        return {
            "connect_is_connected": False,
            "conn_name": 'Мертво',
            "user_name": current_user.name if current_user.is_authenticated else ''
        }


@routes.route('/')
def hello_world():
    return render_template('index.html', **get_context())


@routes.route('/connect')
def connect():
    conn = CONNECTION.reconect()
    context = get_context()
    if conn:
        context['reconectsuccess'] = True
    else:
        context['reconectsuccess'] = False

    return render_template('reconnect.html', **context)


@routes.route('/cmd1', methods=['GET', 'POST'])
def cmd1():
    if request.method == 'GET':
        return render_template('cmd1.html', **get_context())
    if request.method == 'POST':
        conn = CONNECTION.get_connection()
        if conn:
            res = conn.exec_command_sync(userCommandsImpl.command1).to_serializable_dict()
            return jsonify(res)
    raise Exception('no connection')


@routes.route('/cmd3', methods=['GET', 'POST'])
def cmd3():
    if request.method == 'GET':
        return render_template('cmd3.html', **get_context())
    if request.method == 'POST':
        conn = CONNECTION.get_connection()
        if conn:
            content = dict(
                value1=request.form.get('value1', ''),
                value2=int(request.form.get('value2') if request.form.get('value2') else 0),
                value3=float(request.form.get('value3') if request.form.get('value3') else 0),
                value4=int(request.form.get('value4') if request.form.get('value4') else 0)
            )
            res = conn.exec_command_sync(userCommandsImpl.command3, content)
            res = res.get_content()
            return jsonify(res)
    raise Exception('no connection')

