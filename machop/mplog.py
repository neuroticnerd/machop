import colorama
import logging
import multiprocessing
import threading

"""
http://plumberjack.blogspot.com/2010/09/using-logging-with-multiprocessing.html

def _proc_wrapper(queue, func, *args, **kwargs):
    # set default logging class or other things here
    func(*args, **kwargs)

def logged_process(logqueue, target, args=None):
    wrapper_args = [logqueue, target]
    wrapper_args.extend(args if args else [])
    proc = multiprocessing.Process(target=_proc_wrapper, args=wrapper_args)
"""


class QueueHandler(logging.Handler):
    """ sends log records to a multiprocessing queue for handling """

    def __init__(self, queue):
        """ make sure we know what queue to send to """
        logging.Handler.__init__(self)
        self.queue = queue

    def emit(self, record):
        """ sends a log record to the queue """
        try:
            ei = record.exc_info
            if ei:
                self.format(record)
                record.exc_info = None
            self.queue.put_nowait(record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class MPLogger(object):

    def _configure_log(self, origin=None, daemon=False):
        self.log_name = 'machop'
        if daemon:
            self.log_name = 'machop.daemon'
        self.log_origin = origin if origin else 'none'
        self.log_prefix = ''
        self.log_format = self.log_prefix
        if getattr(self, 'log_time', False) is True:
            self.log_format += "[" + self.magenta("%(asctime)s") + "] "
        self.log_format += self.cyan("%(name)s", True)
        self.log_format += self.bright("") + "|"
        self.log_format += self.cyan("%(origin)s", False)
        self.log_format += " %s " % self.blue("$", True)
        self.log_format += "%(message)s"
        self.log_time = "%H:%M:%S"
        if getattr(self, 'log_date', False) is True:
            self.log_time = "%Y-%m-%d %s" % self.log_time
        self.log_handler = None

    def _get_logger(self, queue=None, daemon=False):
        log = logging.getLogger(self.log_name)
        log.propagate = False
        log.setLevel(logging.DEBUG)
        if log.handlers == []:
            if daemon:
                cformat = logging.Formatter(self.log_format, self.log_time)
                console = logging.StreamHandler()
                console.setLevel(logging.DEBUG)
                console.setFormatter(cformat)
                log.addHandler(console)
                self.log_handler = console
            elif queue:
                qformat = logging.Formatter(self.log_format, self.log_time)
                qhandler = QueueHandler(queue)
                qhandler.setLevel(logging.DEBUG)
                qhandler.setFormatter(qformat)
                log.addHandler(qhandler)
                self.log_handler = qhandler
            else:
                raise ValueError("either 'queue' or 'daemon' is required!")
        elif len(log.handlers) > 1:
            raise ValueError("log has too many handlers!")
        else:
            self.log_handler = log.handlers[0]
        self.log = log

    @classmethod
    def bright(cls, text, reset=True):
        result = colorama.Style.BRIGHT
        result += text
        if reset:
            result += colorama.Style.RESET_ALL
        return result

    @classmethod
    def red(cls, text, bright=False, reset=True):
        result = colorama.Fore.RED
        if bright:
            result += colorama.Style.BRIGHT
        result += text
        if reset:
            result += colorama.Style.RESET_ALL
        return result

    @classmethod
    def cyan(cls, text, bright=False, reset=True):
        result = colorama.Fore.CYAN
        if bright:
            result += colorama.Style.BRIGHT
        result += text
        if reset:
            result += colorama.Style.RESET_ALL
        return result

    @classmethod
    def blue(cls, text, bright=False, reset=True):
        result = colorama.Fore.BLUE
        if bright:
            result += colorama.Style.BRIGHT
        result += text
        if reset:
            result += colorama.Style.RESET_ALL
        return result

    @classmethod
    def yellow(cls, text, bright=False, reset=True):
        result = colorama.Fore.YELLOW
        if bright:
            result += colorama.Style.BRIGHT
        result += text
        if reset:
            result += colorama.Style.RESET_ALL
        return result

    @classmethod
    def green(cls, text, bright=False, reset=True):
        result = colorama.Fore.GREEN
        if bright:
            result += colorama.Style.BRIGHT
        result += text
        if reset:
            result += colorama.Style.RESET_ALL
        return result

    @classmethod
    def magenta(cls, text, bright=False, reset=True):
        result = colorama.Fore.MAGENTA
        if bright:
            result += colorama.Style.BRIGHT
        result += text
        if reset:
            result += colorama.Style.RESET_ALL
        return result


class MachopLogDaemon(threading.Thread, MPLogger):

    def create_queue(self):
        queue = multiprocessing.Queue()
        self.queue = queue

    def run(self):
        self.log_time = True
        self._configure_log('daemon', True)
        self._get_logger(daemon=True)
        while True:
            try:
                record = self.queue.get()
                if record is None:
                    break
                noformat = getattr(record, 'noformat', False)
                if noformat:
                    nfmt = self.log_prefix + "%(message)s"
                    self.log_handler.setFormatter(logging.Formatter(nfmt))
                self.log.handle(record)
                if noformat:
                    fm = logging.Formatter(self.log_format, self.log_time)
                    self.log_handler.setFormatter(fm)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                import sys
                import traceback
                print >> sys.stderr, 'FATAL: logging error! '
                traceback.print_exc(file=sys.stderr)


class MachopLog(MPLogger):

    def __init__(self, logqueue, origin=None):
        self.queue = logqueue
        self._configure_log(origin if origin else "none")
        self._get_logger(queue=self.queue)

    def context(self, context=None):
        previous = self.log_origin
        if context:
            if previous.find("(") > 0:
                temp = previous[:previous.find("(")]
                self.log_origin = temp + "(%s)" % context
            else:
                self.log_origin = self.log_origin + "(%s)" % context
            self.log_origin = context
        return previous

    def out(self, message, noformat=False):
        self.log.info(message, extra={
            'noformat': noformat,
            'origin': self.log_origin,
            })

    def nl(self):
        self.out('', noformat=True)
