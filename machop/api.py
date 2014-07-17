
import os
import subprocess as sp

from .utils import iscallable, ensure_list, unbuffered, invalid_command
from .watch import MachopWatchCommand
from .async import MachopAsyncCommand
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


def _get_callable(command):
    if not iscallable(command):
        ccmd = __move_list__.get(command, None)
        if not ccmd:
            raise KeyError("command %s not found" % command)
        return ccmd
    return command


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
        cmdlog = MachopLog(_api_q, 'run')
        if cmdpath:
            result = action(cmdpath=cmdpath, log=cmdlog, *args, **kwargs)
            continue
        result = action(log=cmdlog, *args, **kwargs)
        if result:
            pass
    # @@@ raise exceptions or log for error results?


def watch(globpatterns, commandchain):
    """
    watch accepts glob-style pattern(s) as a list which are then monitored
    for modifications, at which point commandchain is executed. commandchain
    is a single or list of functions or registered commands.
    """
    log = MachopLog(_api_q, 'watch.launcher')
    globs = ensure_list(globpatterns)
    commands = _get_callables(ensure_list(commandchain))
    try:
        cwd = CURRENT_DIRECTORY
        watchman = MachopWatchCommand(globs, commands, cwd, _api_q)
        watchman.start()
        __join_list__.append(watchman)
        return False
    except Exception as e:
        msg = log.red("fatal exception:", True)
        msg += "\n %s" % e
        log.out(msg)
    return True


def async(commands):
    """
    commands must be a list of functions or registered commands, or a dict
    where the keys are process names and the values are individual commands
    """
    if isinstance(commands, dict):
        for name, cmd in commands.iteritems():
            ccmd = _get_callable(cmd)
            cmdproc = MachopAsyncCommand(ccmd, CURRENT_DIRECTORY, _api_q, name)
            cmdproc.start()
            __join_list__.append(cmdproc)
        return
    commands = _get_callables(ensure_list(commands))
    for cmd in commands:
        cmdproc = MachopAsyncCommand(cmd, CURRENT_DIRECTORY, _api_q)
        cmdproc.start()
        __join_list__.append(cmdproc)


def shell(command, realtime=None, shell=True):
    """ runs a shell command using subprocess.Popen """
    log = MachopLog(_api_q, 'shell')
    exit = -1
    stdout = None
    stderr = None
    try:
        proc = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, shell=shell)
        if realtime is True:
            for line, stream in unbuffered(proc, True):
                log.out(line)
        elif realtime:
            for line, stream in unbuffered(proc, True):
                realtime(line, stream)
        else:
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
        return (exit, stdout, stderr)
    except KeyboardInterrupt:
        cmd = log.yellow(command[0], True) if command else None
        log.out("KeyboardInterrupt: %s terminated" % cmd)
    except Exception as e:
        import traceback
        cmd = log.yellow(command[0], True) if command else None
        msg = log.red("fatal exception: %s terminated" % cmd, True)
        msg += "\n %s" % traceback.format_exc()
        log.out(msg)
    return (exit, stdout, stderr)
    # @@@ just return the spent process instead?


def _command_wait(log, timeout=1, killwait=2, kill=False):
    """ waits for async processes while stopping for interrupts and exits """

    def cleanup(killtimeout):
        for strand in __join_list__:
            # @@@ use event signal to attempt termination
            strand.join(killtimeout)
            strand.terminate()
            log.out(log.red("terminated:", True) + " %s" % strand)

    if kill:
        cleanup(0)
        return
    try:
        while __join_list__:
            strand = __join_list__[0]
            if strand.is_alive():
                strand.join(timeout)
            else:
                __join_list__.remove(strand)
    except (KeyboardInterrupt, SystemExit):
        log.out("shutting down...")
        cleanup(killwait)
    except:
        cleanup(0)
        raise
