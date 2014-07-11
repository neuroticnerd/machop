
import multiprocessing
from .commands import MachopCommand


class MachopAsyncCommand(MachopCommand, multiprocessing.Process):

    def __init__(self, command=None):
        self.command = command
        super(MachopAsyncCommand, self).__init__()

    def run(self):
        if self.command:
            self.command()
