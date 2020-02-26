"""модуль содержит всю локигу логирования

ЗЫ тут я особо пока вообще не парился"""


import logging
from pyproto.pyproto.config import MAX_LOG_LENGHT

LOG_FILE_NAME = 'app.log'


def set_logging_config(folder='', file_name=LOG_FILE_NAME):
    logging.basicConfig(
        filename=folder + file_name,
        filemode='a',
        format='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
        level=logging.INFO)


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