from django.apps import AppConfig
from tcpClientModule.client import StrongClient

clientObj = None


class TcpCLientConfig(AppConfig):
    name = 'tcpClientModule'

    def __init__(self, app_name, app_module):
        global clientObj
        if clientObj is None:
            clientObj = StrongClient()
        super().__init__(app_name, app_module)

    def ready(self):
        if clientObj is not None:
            clientObj.start()
