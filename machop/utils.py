import contextlib
import imp
import os


def import_config(path=None):
    """ dynamically imports 'karatechop.py' """
    CONFIG_MODULE = 'karatechop'
    karatechop = None
    path = path if path else os.getcwd()
    try:
        meta = imp.find_module(CONFIG_MODULE, [path])
        if meta[0]:
            cfgfile = meta[0]
        karatechop = imp.load_module(CONFIG_MODULE, *meta)
    except (ImportError, IOError):
        pass
    finally:
        try:
            cfgfile.close()
        except:
            pass
    return karatechop


def unbuffered(process, streamname=None, ignoreempty=True):
    """
    http://stackoverflow.com/questions/803265/
        getting-realtime-output-using-subprocess
    """
    streamname = streamname if streamname else 'stdout'
    stream = getattr(process, streamname)
    newlines = ['\n', '\r\n', '\r']
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
            if len(out) > 0 and out[-1] in newlines:
                out = out[:-1]
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
