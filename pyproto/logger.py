'''модуль содержит всю локигу логирования

ЗЫ тут я особо пока вообще не парился'''
import logging
from pyproto.pyproto.config import MAX_LOG_LENGHT

BASE_FOLDER = ''
LOG_FILE_NAME = 'app.log'


def reset_config(folder, file_name):
    global BASE_FOLDER
    global LOG_FILE_NAME
    BASE_FOLDER = folder
    LOG_FILE_NAME = file_name
    logging.basicConfig(
        filename=BASE_FOLDER + LOG_FILE_NAME,
        filemode='a',
        format='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
        level=logging.INFO)


reset_config(BASE_FOLDER, LOG_FILE_NAME)


def msg_handler(decor_func):
    def wrapper(msg):
        msg = msg[:MAX_LOG_LENGHT]
        print(msg)  # закоментировать тут, чтоб убрать вывод в консоль
        decor_func(msg)
    return wrapper


@msg_handler
def write_info(msg):
    logging.info(msg)


@msg_handler
def write_error(msg):
    logging.error(msg)