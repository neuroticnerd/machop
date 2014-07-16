# -*- coding: utf-8 -*-
import sys
import os

from .strings import ascii_machop, ascii_fainted, ascii_choose_you
from .strings import ascii_runaway
from .strings import txt_startup_msg, txt_config_error
from .mplog import MachopLog, MachopLogDaemon
from .api import run, _command_wait
from .utils import initialize_process


class MachopCLI(object):
    """ creates and manages the CLI for machop """

    def setup(self, path=None):
        self.args = sys.argv[1:]
        self.exitstatus = 0
        self.path = path if path else os.getcwd()
        self.daemon = MachopLogDaemon()
        self.daemon.create_queue()
        result = initialize_process(self.path, self.daemon.queue)
        self.daemon.start()
        self.log = MachopLog(self.daemon.queue, origin='main')
        if result:
            errmsg = txt_config_error
            if result != '':
                errmsg += "\n\n" + result
            self.log.out(errmsg)
            self.exitstatus = 1
            self.daemon.queue.put_nowait(None)
            return True
        return False

    def runcli(self, path=None):
        if self.setup(path):
            return
        try:
            if len(self.args) > 0:
                # running specific commands
                # self.log.out("\n" + ascii_machop, noformat=True)
                for command in self.args:
                    # @@@ TODO use argparse to config params to commands
                    run(command, cmdpath=self.path)
                _command_wait(self.log)
            else:
                # running default command
                self.log.out(ascii_choose_you, noformat=True)
                self.log.out(ascii_machop, noformat=True)
                self.log.out(txt_startup_msg, noformat=True)
                # @@@ TODO use argparse to config params to commands
                run('focus-energy', cmdpath=self.path)
                _command_wait(self.log)
                self.log.out(ascii_runaway, True)
        except Exception:
            self.log.out(ascii_fainted, True)
            _command_wait(self.log, kill=True)
            import traceback
            errmsg = self.log.red("fatal exception", True) + " :\n"
            errmsg += traceback.format_exc()
            self.log.out(errmsg)
        self.daemon.queue.put_nowait(None)
        self.daemon.join(1)
        raise SystemExit(self.exitstatus)
