
import imp
import os
import sys
import multiprocessing
import colorama

from contextlib import closing as cclosing


def invalid_command(cmdname, cmdlist=None):
    from .mplog import MachopLog as color
    msg = color.red("fatal error:", True)
    msg += " %s is not a registered command!" % color.yellow(cmdname, True)
    if cmdlist is not None:
        msg += "\n valid commands are:"
        for cmd in cmdlist:
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


def unbuffered(process, ignoreempty=True, strip=False):
    """
    http://stackoverflow.com/questions/803265/
        getting-realtime-output-using-subprocess

    *** only works for stdout and stderr as PIPEs currently
    *** does not look for '\r' because screw old macs
    """
    newlines = ['\n', '\r\n']
    procout = getattr(process, 'stdout')
    procerr = getattr(process, 'stderr')
    with cclosing(procout) as stdout, cclosing(procerr) as stderr:
        while True:
            out = []
            stream = None
            streamname = None
            laststderr = stderr.read(1)
            laststdout = stdout.read(1)
            last = None
            while True:
                if laststderr != '':
                    stream = stderr
                    streamname = 'stderr'
                    last = laststderr
                    break
                elif laststdout != '':
                    stream = stdout
                    streamname = 'stdout'
                    last = laststdout
                    break
                if process.poll() is not None:
                    if laststderr == '' and laststdout == '':
                        last = ''
                        break
                laststderr = stderr.read(1)
                laststdout = stdout.read(1)
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
            yield (out, streamname)


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
