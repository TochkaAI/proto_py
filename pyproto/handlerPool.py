from .baseCommands import BaseCommand


class HandlerPool(list):
    def __init__(self):
        super().__init__()

    def add_command(self, command: BaseCommand):
        self.append(command.COMMAND_UUID)

    def is_catched(self, command: BaseCommand):
        if command.COMMAND_UUID in self:
            return True
        return False

    def remove_command(self, command: BaseCommand):
        if command.COMMAND_UUID in self:
            self.remove(command.COMMAND_UUID)
