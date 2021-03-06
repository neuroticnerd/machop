
import imp
import os
import sys
import multiprocessing
import colorama
import contextlib
import subprocess
import threading


def invalid_command(cmdname, cmdlist=None):
    from .mplog import MachopLog as color
    msg = ""
    if cmdname is not None:
        ylwcmd = color.yellow(cmdname, True)
        msg = color.red("fatal error:", True)
        msg += " %s is not a registered command!\n" % ylwcmd
    if cmdlist is not None:
        msg += " valid machop commands are:"
        for cmd in cmdlist:
            if cmd != 'focus-energy':
                msg += "\n - %s" % color.yellow(cmd, True)
    return msg


def wait_for_interrupt(parallel, timeout=1, reraise=False):
    """
    In Python running processes (threads specifically) do not respond to
    interrupt events if .join() or similar is called, so this can be used to
    poll (with a timeout) while also catching interrupt and exit events. This
    also means that any unhandled exceptions normally blocked by .join() will
    bubble up in between polling.
    """
    try:
        while parallel.is_alive():
            parallel.join(timeout)
    except (KeyboardInterrupt, SystemExit):
        if reraise:
            raise
    return parallel


class ShellResult(object):
    def __init__(self, process=None, stdout=None, stderr=None):
        self.proc = process
        self.stdout = stdout
        self.stderr = stderr

    @property
    def exit(self):
        return self.proc.returncode if self.proc is not None else None


class OutputLine(object):
    def __init__(self, streamname, line):
        self.stream = streamname
        self.line = line


class PopenPiped(subprocess.Popen):
    """
    http://stackoverflow.com/questions/375427/
        non-blocking-read-on-a-subprocess-pipe-in-python/4896288#4896288
    http://stefaanlippens.net/python-asynchronous-subprocess-pipe-reading
    """
    def __init__(self, command, stdout=None, stderr=None, **kwargs):
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE
        super(PopenPiped, self).__init__(
            command, stdout=stdout, stderr=stderr, **kwargs)

    def _q_unbuffered(self, process, stream, queue, ignoreempty=False):
        streamname = stream
        stream = getattr(process, stream)
        while True:
            out = []
            last = stream.read(1)
            if last == '' and self.poll() is not None:
                break
            while True:
                if last == '' and self.poll() is not None:
                    break
                out.append(last)
                if ''.join(out[-2:]).find(os.linesep) != -1 or last == '\n':
                    break
                last = stream.read(1)
            out = ''.join(out)
            out = out.rstrip()
            if out == '' and ignoreempty:
                continue
            queue.put((streamname, out))
        queue.put(None)

    def listen(self):
        if self.poll() is not None:
            return
        q = multiprocessing.Queue()
        t_out = threading.Thread(
            target=self._q_unbuffered, args=(self, 'stdout', q))
        t_out.daemon = True
        t_err = threading.Thread(
            target=self._q_unbuffered, args=(self, 'stderr', q))
        t_err.daemon = True
        t_out.start()
        t_err.start()
        running = 2
        while running > 0:
            try:
                line = q.get()
                if line is None:
                    running = running - 1
                    continue
                if isinstance(line, tuple) and len(line) == 2:
                    yield OutputLine(line[0], line[1])
                else:
                    raise ValueError("unexpected queue element: %s" % line)
            except:
                raise


def unbuffered(process, ignoreempty=True, strip=False, stream=None):
    """
    http://stackoverflow.com/questions/803265/
        getting-realtime-output-using-subprocess

    *** only works for stdout and stderr as PIPEs currently
    *** does not recognize '\r' newlines because screw old macs
    """
    newlines = ['\n', '\r\n']
    stream = getattr(process, stream if stream else 'stdout')
    with contextlib.closing(stream):
        while True:
            out = []
            last = stream.read(1)
            if last == '' and process.poll() is not None:
                break
            while last not in newlines:
                if last == '' and process.poll() is not None:
                    break
                out.append(last)
                last = stream.read(1)
            out = ''.join(out)
            if strip:
                out = out.strip()
            if out == '' and ignoreempty:
                continue
            yield out


def iscallable(obj):
    if hasattr(obj, '__call__'):
        return True
    return False


def ensure_list(obj):
    if not isinstance(obj, (list, tuple)):
        return [obj]
    return obj


def _import_config(path=None, trace=False):
    """
    dynamically imports 'karatechop.py'

    we check sys.modules first since load_module() is effectively a reload()
    which is not what we want since it will re-run any code in the config
    """
    CONFIG_MODULE = 'karatechop'
    if CONFIG_MODULE in sys.modules.keys():
        return sys.modules[CONFIG_MODULE]
    path = path if path else os.getcwd()
    try:
        (ofile, fname, data) = imp.find_module(CONFIG_MODULE, [path])
        ext = os.path.splitext(fname)[-1]
        if ext != '.py':
            from .mplog import MachopLog
            yfname = MachopLog.yellow(fname)
            raise ImportError("cannot use stale object code %s" % yfname)
        imp.load_module(CONFIG_MODULE, ofile, fname, data)
    except ImportError as e:
        if trace:
            import traceback
            return traceback.format_exc()
        from .mplog import MachopLog
        return MachopLog.red("ImportError", True) + ": %s" % e
    finally:
        try:
            ofile.close()
        except:
            pass
    return None


def initialize_process(cfgpath, queue):
    """
    This function initializes a process by loading the config file as well as
    setting the queue for logging from api calls. It also makes sure colorama
    is initialized for ANSI terminal output.
    """
    colorama.init()
    from .api import _set_api_q
    _set_api_q(queue)
    return _import_config(cfgpath)


class PickleHolder(object):
    def __init__(self, call, *args):
        self.ret = (call, args)

    def __reduce__(self):
        return self.ret

    def __call__(self, *args, **kw):
        msg = "PickleHolder objects should never be called directly!"
        raise NotImplementedError(msg)


class MachopProcess(multiprocessing.Process):
    """
    This should be inherited from instead by any class which wants to inherit
    from multiprocessing.Process to make sure that karatechop.py is dynamically
    loaded prior to the process starting, thus ensuring that any callables
    defined in the config file are available.

    *** classes using this mixin must call _safe_process() before running!
    *** this mixin must be inherited last to ensure this __reduce__ is called!
    """
    def _safe_process(self, queue, cfgpath, init=None):
        """
        The init param here is a tuple containing anything required by this
        class's __init__() to recreate it after being pickled then coming out
        on the other end. This function should be called within __init__()
        otherwise an exception could be raised!
        """
        cfgpath = cfgpath if cfgpath else os.getcwd()
        self._safe_process_args = (cfgpath, queue)
        self._pickled_obj_args = init = init if init else ()

    def __reduce__(self):
        """
        A copy of the instance class is created during the below code to
        avoid issues with duplicate assertions in the pickle module. While it
        does add additional overhead, if objcopy were simply replaced with self
        then the pickle module will see the result of this function and that
        of the reduction of self as identical and raise an AssertionError

        @@@ is there any way to capture the output of initialize_process?
        """
        params = getattr(self, '_pickled_obj_args', None)
        cfgargs = getattr(self, '_safe_process_args', None)
        reduction = getattr(self, '_is_being_reduced', False)
        if reduction and params:
            return (self.__class__, params)
        elif reduction:
            raise ValueError("init args cannot be found for process!")
        self._is_being_reduced = True
        if not cfgargs:
            raise ValueError("process is not safe!")
        objcopy = self.__class__(*params)
        objcopy._is_being_reduced = True
        tpl = (
            PickleHolder(getattr, tuple, '__getitem__'),
            ((PickleHolder(initialize_process, *cfgargs), objcopy), -1)
            )
        return tpl
