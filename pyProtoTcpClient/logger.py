'''модуль содержит всю локигу логирования

ЗЫ тут я особо пока вообще не парился'''
import logging
# from logging.handlers import TimedRotatingFileHandler

logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
    level=logging.INFO)


def print_console_decor(decor_func):
    def wrapper(msg):
        print(msg)  # закоментировать тут, чтоб убрать вывод в консоль
        decor_func(msg)
    return wrapper


@print_console_decor
def write_info(msg):
    logging.info(msg)


@print_console_decor
def write_error(msg):
    logging.error(msg)