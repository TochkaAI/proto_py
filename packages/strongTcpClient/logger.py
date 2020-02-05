'''модуль содержит всю локигу логирования

ЗЫ тут я особо пока вообще не парился'''
import logging
# from logging.handlers import TimedRotatingFileHandler

logging.basicConfig(
    filename='flask_web_app/app.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
    level=logging.INFO)


def write_info(msg):
    print(msg)
    logging.info(msg)


# def initLogging():
#     logger = logging.getLogger('simple')
#     logname = "my_app.log"
#     fh = logging.FileHandler(logname)
#
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     fh.setFormatter(formatter)
#
#     logging.basicConfig(filename=logname, level=logging.INFO)
#     handler = TimedRotatingFileHandler(logname, when="midnight", interval=1)
#     handler.suffix = "%Y%m%d"
#     logger.addHandler(handler)
