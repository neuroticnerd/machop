
import os
import subprocess as sp

from .utils import iscallable, ensure_list
from .async import MachopAsyncCommand
from .watch import MachopWatchCommand
from .strings import invalid_command
from .mplog import MachopLog

_api_q = None


def _set_api_q(queue):
    global _api_q
    _api_q = queue


def _leer(*args, **kwargs):
    # _log.out("no default command has been set!")
    pass


def machop_init(*args, **kwargs):
    # _log.out("this will initialize a karatechop.py file in cwd")
    pass


CURRENT_DIRECTORY = os.getcwd()
__join_list__ = []
__move_list__ = {'focus-energy': _leer, 'init': machop_init}


def _get_callables(cmdlist):
    commands = []
    for cmd in cmdlist:
        if not iscallable(cmd):
            entry = __move_list__.get(cmd, None)
            if not entry:
                raise KeyError("command %s not found" % cmd)
            commands.extend(_get_callables(ensure_list(entry)))
        else:
            commands.append(cmd)
    return commands


def default(defaultcommands):
    command('focus-energy', defaultcommands)


def command(cmdstring, cmdfunction):
    # @@@ TODO: validate command names before adding!
    cmdfunction = ensure_list(cmdfunction)
    __move_list__[cmdstring] = cmdfunction


def run(command, *args, **kwargs):
    log = MachopLog(_api_q, 'run')
    if not __move_list__.get(command, None):
        log.out(invalid_command(command, __move_list__.keys()))
        return
    actions = ensure_list(__move_list__[command])
    cmdpath = None
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
            result = action(cmdpath=cmdpath, log=log, *args, **kwargs)
            continue
        result = action(*args, **kwargs)
        if result:
            pass
    # @@@ raise exceptions or log for error results?


def async(commands, shell=False):
    """
    commands must be a list of functions or registered commands
    *** if you want async shells use machop.shell([...], async=True)
    ***  ^ not yet supported
    """
    commands = _get_callables(ensure_list(commands))
    for cmd in commands:
        cmdproc = MachopAsyncCommand(cmd, CURRENT_DIRECTORY, _api_q)
        cmdproc.start()
        __join_list__.append(cmdproc)


def watch(globpatterns, commandchain):
    """
    watch accepts glob-style pattern(s) as a list which are then monitored
    for modifications, at which point commandchain is executed. commandchain
    is a single or list of functions or registered commands.
    """
    globs = ensure_list(globpatterns)
    commands = _get_callables(ensure_list(commandchain))
    watchman = MachopWatchCommand(globs, commands, CURRENT_DIRECTORY)
    watchman.set_queue(_api_q)
    watchman.start()
    __join_list__.append(watchman)


def shell(command, shell=False):
    """
    does not support async yet!
    """
    log = MachopLog(_api_q, 'shell')
    try:
        proc = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, shell=shell)
        stdout, stderr = proc.communicate()
        exit = proc.returncode
    except OSError as e:
        if e.errno != 2:
            raise
        msg = log.red("fatal exception: OSError[%s]" % e.errno, True)
        msg += "\n the command "
        msg += log.yellow(command[0], True) if command else None
        msg += " is not valid or could not be found!\n "
        msg += log.yellow(command[0], True) if command else None
        msg += " parameters: "
        if len(command) > 1:
            msg += log.yellow(' '.join(command[1:]))
        msg += "\n"
        log.out(msg)
        return (-1, None, None)
    return (exit, stdout, stderr)
    # @@@ just return the spent process


def _wait():
    log = MachopLog(_api_q, 'main')
    try:
        while __join_list__:
            strand = __join_list__[0]
            if strand.exitcode is None:
                strand.join(1)
            else:
                strand.cleanup()
                __join_list__.remove(strand)
    except KeyboardInterrupt:
        log.out("shutting down...")
        for strand in __join_list__:
            strand.shutdown()
            strand.join(2)
            strand.terminate()
