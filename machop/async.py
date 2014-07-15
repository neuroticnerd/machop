
import multiprocessing

from .commands import MachopCommand
from .mplog import MachopLog


class MachopAsyncCommand(MachopCommand, multiprocessing.Process):

    def __init__(self, command, path, queue):
        self.command = command
        self.queue = queue
        self.path = path
        super(MachopAsyncCommand, self).__init__()

    def run(self):
        log = MachopLog(self.queue, 'async')
        if self.command:
            try:
                self.command(cmdpath=self.path, log=log)
            except:
                import traceback as tb
                log.out(log.red("fatal error!\n", True) + tb.format_exc())
