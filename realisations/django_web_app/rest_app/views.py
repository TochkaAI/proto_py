from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse

from singleton_tcp import userCommandsImpl
from singleton_tcp.config import CONNECTION


def get_context():
    if CONNECTION:
        return {
            "conn_name": CONNECTION.getpeername(),
            "requests": CONNECTION.request_pool,
            "answer": CONNECTION.message_pool
        }
    else:
        return {}


def index(request):
    return render(request, 'index.html', get_context())


def cmd1(request):
    if request.method == 'GET':
        return render(request, 'cmd1.html', get_context())
    elif request.method == 'POST':
        if CONNECTION:
            res = CONNECTION.exec_command_sync(userCommandsImpl.command1).to_serializable_dict()
            return JsonResponse(res)


def cmd3(request):
    if request.method == 'GET':
        return render(request, 'cmd3.html', get_context())
    elif request.method == 'POST':
        if CONNECTION:
            res = CONNECTION.exec_command_sync(userCommandsImpl.command3, request.POST)
            return JsonResponse(res.get_content())
