
from .mplog import MachopLog
from .utils import MachopProcess


class MachopAsyncCommand(MachopProcess):

    def __init__(self, func, path, queue, name=None, trace=False):
        super(MachopAsyncCommand, self).__init__()
        recreate = (func, path, queue, name, trace)
        self._safe_process(queue=queue, cfgpath=path, init=recreate)
        self.command = func
        self.queue = queue
        self.path = path
        self.trace = trace
        self.pname = name

    def run(self):
        log = MachopLog(self.queue, 'async')
        try:
            pname = log.yellow(self.pname, True) if self.pname else "process"
            log.out("starting %s..." % pname)
            self.command(cmdpath=self.path, log=MachopLog(self.queue, 'async'))
            log.out("%s completed\n" % pname)
        except Exception as e:
            if self.trace:
                import traceback as tb
                log.out(log.red("fatal error!\n", True) + tb.format_exc())
            else:
                msg = log.red("fatal exception:", True)
                msg += "\n %s" % e
                log.out(msg)
