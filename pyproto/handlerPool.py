from .baseCommands import BaseCommand


class HandlerPool(set):
    def __init__(self):
        super().__init__()

    def add_command(self, command: BaseCommand):
        self.add(command.COMMAND_UUID)

    def is_catching(self, command_uuid):
        if command_uuid in self:
            return True
        return False

    def remove_command(self, command: BaseCommand):
        """

        :type command: BaseCommand
        """
        if command.COMMAND_UUID in self:
            self.remove(command.COMMAND_UUID)
