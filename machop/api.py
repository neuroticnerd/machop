
import os
import glob
import time

from .core import iscallable, ensure_list
from .async import MachopAsyncCommand
from .watch import MachopWatchCommand

CURRENT_DIRECTORY = os.getcwd()
__join_list__ = []
__move_list__ = {}


def command(cmdstring, cmdfunction):
    # @@@ TODO: validate command names before adding!
    if not isinstance(cmdfunction, (list, tuple)):
        cmdfunction = [cmdfunction]
    __move_list__[cmdstring] = cmdfunction


def default(defaultcommands):
    command('focus-energy', defaultcommands)


def run(command, *args, **kwargs):
    if not __move_list__.get(command, None):
        print "%s is not a registered command!" % command
        return
    actions = __move_list__[command]
    cmdpath = None
    if not isinstance(actions, (list, tuple)):
        actions = [actions]
    # @@@ determine if the action is a callable, or another command to run
    if 'cmdpath' not in kwargs.keys():
        cmdpath = CURRENT_DIRECTORY
    for action in actions:
        if not hasattr(action, '__call__'):
            if not cmdpath:
                run(action, *args, **kwargs)
            else:
                run(action, cmdpath, *args, **kwargs)
            continue
        result = None
        if cmdpath:
            result = action(cmdpath=cmdpath, *args, **kwargs)
            continue
        result = action(*args, **kwargs)
        if result:
            pass
    # @@@ raise exceptions or log for error results?


def async(commands, shell=False):
    """
    commands must be a list of callables or registered commands
    *** if you want async shells use machop.shell([...], async=True)
    """
    commands = ensure_list(commands)
    if not iscallable(command):
        raise TypeError
    cmdproc = MachopAsyncCommand(commands)
    cmdproc.start()
    __join_list__.append(cmdproc)


def watch(globpatterns, commandchain):
    commands = ensure_list(commandchain)
    globs = ensure_list(globpatterns)
    # @@@ get actual command objects or ensure string list
    watchman = MachopWatchCommand(globs, commands, CURRENT_DIRECTORY, run)
    watchman.start()
    __join_list__.append(watchman)


def _wait():
    try:
        while __join_list__:
            strand = __join_list__[0]
            if strand.exitcode is None:
                strand.join(1)
            else:
                strand.cleanup()
                __join_list__.remove(strand)
    except KeyboardInterrupt:
        print "shutting down..."
        for strand in __join_list__:
            strand.shutdown()
            strand.join(2)
            strand.terminate()
        print "machop fainted!"


def _leer(*args, **kwargs):
    print "no default command has been set!"

# make sure there's a default command available regardless
default(_leer)
