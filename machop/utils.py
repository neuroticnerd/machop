import colorama
import logging

colorama.init()


def iscallable(obj):
    if hasattr(obj, '__call__'):
        return True
    return False


def ensure_list(obj):
    if not isinstance(obj, (list, tuple)):
        return [obj]
    return obj


class MachopLogger(object):
    def __init__(self, origin=None):
        self.origin = origin if origin else "none"
        self.logname = "machop"
        self._make_colors()
        self.logformat = self.cyan_br + "%(name)s" + self.reset
        self.logformat += "(" + self.dim + self.magenta + "%(asctime)s"
        self.logformat += self.reset + ")@"
        self.logformat += self.blue_br + "%(origin)s" + self.reset + " | "
        self.logformat += "%(message)s"
        self.logtime = "%Y-%m-%d %H:%M:%S"
        self.handler = None
        self._get_logger()

    def _make_colors(self):
        self.red_br = colorama.Fore.RED + colorama.Style.BRIGHT
        self.red = colorama.Fore.RED
        self.cyan_br = colorama.Fore.CYAN + colorama.Style.BRIGHT
        self.cyan = colorama.Fore.CYAN
        self.blue_br = colorama.Fore.BLUE + colorama.Style.BRIGHT
        self.blue = colorama.Fore.BLUE
        self.yellow_br = colorama.Fore.YELLOW + colorama.Style.BRIGHT
        self.yellow = colorama.Fore.YELLOW
        self.green_br = colorama.Fore.GREEN + colorama.Style.BRIGHT
        self.green = colorama.Fore.GREEN
        self.magenta_br = colorama.Fore.MAGENTA + colorama.Style.BRIGHT
        self.magenta = colorama.Fore.MAGENTA
        self.dim = colorama.Style.DIM
        self.reset = colorama.Style.RESET_ALL

    def _get_logger(self):
        log = logging.getLogger(self.logname)
        log.propagate = False
        if log.handlers == []:
            log.setLevel(logging.DEBUG)
            cformat = logging.Formatter(self.logformat, self.logtime)
            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG)
            console.setFormatter(cformat)
            log.addHandler(console)
            self.handler = log.handlers[0]
        elif len(log.handlers) > 1:
            log.critical("this logger has multiple handlers!")
            self.handler = log.handlers[0]
        else:
            self.handler = log.handlers[0]
        self.log = log

    def out(self, message, noformat=False):
        if noformat:
            self.handler.setFormatter(logging.Formatter())
            self.log.info(message, extra={'origin': self.origin})
            formatter = logging.Formatter(self.logformat, self.logtime)
            self.handler.setFormatter(formatter)
            return
        self.log.info(message, extra={'origin': self.origin})

    def nl(self):
        self.out('\n', noformat=True)
