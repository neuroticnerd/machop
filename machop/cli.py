# -*- coding: utf-8 -*-
import sys
import os
import imp

from .strings import ascii_machop, ascii_fainted, ascii_choose_you
from .strings import ascii_runaway
from .strings import txt_startup_msg, txt_config_error
from .mplog import MachopLog, MachopLogDaemon
from .api import _set_api_q, run, _command_wait


class MachopCLI(object):
    """ creates and manages the CLI for machop """
    CONFIG_MODULE = 'karatechop'
    CONFIG_FILENAME = CONFIG_MODULE + '.py'

    def setup(self, path=None):
        self.args = sys.argv[1:]
        self.exitstatus = 0
        self.karatechop = None
        self.path = path
        if not self.path:
            self.path = os.getcwd()
        elif self.path != os.getcwd():
            raise ValueError("process paths not equal!")
        self.daemon = MachopLogDaemon()
        self.daemon.create_queue()
        _set_api_q(self.daemon.queue)
        self.daemon.start()
        self.log = MachopLog(self.daemon.queue, origin='main')

    def runcli(self, path=None):
        self.setup(path)
        try:
            meta = ('.py', 'rb', imp.PY_SOURCE)
            filepath = os.path.join(self.path, self.CONFIG_FILENAME)
            with open(filepath, 'rb') as kfile:
                cfgmod = self.CONFIG_MODULE
                karatechop = imp.load_module(cfgmod, kfile, filepath, meta)
                if not karatechop:
                    raise ValueError("error accessing karatechop module")
        except (ImportError, IOError):
            self.log.out(txt_config_error)
            self.exitstatus = 1
            raise SystemExit(self.exitstatus)
        try:
            if len(self.args) > 0:
                # running specific commands
                # self.log.out("\n" + ascii_machop, noformat=True)
                for command in self.args:
                    # @@@ TODO use argparse to config params to commands
                    run(command, cmdpath=self.path)
                _command_wait()
            else:
                # running default command
                self.log.out(ascii_choose_you, noformat=True)
                self.log.out(ascii_machop, noformat=True)
                self.log.out(txt_startup_msg, noformat=True)
                # @@@ TODO use argparse to config params to commands
                run('focus-energy', cmdpath=self.path)
                _command_wait()
                self.log.out(ascii_runaway, True)
        except Exception:
            self.log.out(ascii_fainted, True)
            import traceback
            self.log.out(traceback.format_exc())
        self.daemon.queue.put_nowait(None)
        self.daemon.join()
        raise SystemExit(self.exitstatus)
