#  {project_root}/{your_app}/__init__.py
# import os
# import signal
# import sys
#
# from tcpClientModule.config import clientObj

default_app_config = 'tcpClientModule.config.TcpCLientConfig'


# def my_signal_handler(*args):
#     if os.environ.get('RUN_MAIN') == 'true':
#         clientObj.isActive = False
#         print('stopped')
#     sys.exit(0)
#
#
# signal.signal(signal.SIGINT, my_signal_handler)
