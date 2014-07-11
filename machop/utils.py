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
        self.logformat = self.cyan("%(name)s", True) + "("
        self.logformat += self.magenta("%(asctime)s") + ")@"
        self.logformat += self.blue("%(origin)s", True) + " | %(message)s"
        self.logtime = "%Y-%m-%d %H:%M:%S"
        self.handler = None
        self._get_logger()

    def red(self, text, bright=False, reset=True):
        result = colorama.Fore.RED
        if bright:
            result += colorama.Style.BRIGHT
        result += text
        if reset:
            result += colorama.Style.RESET_ALL
        return result

    def cyan(self, text, bright=False, reset=True):
        result = colorama.Fore.CYAN
        if bright:
            result += colorama.Style.BRIGHT
        result += text
        if reset:
            result += colorama.Style.RESET_ALL
        return result

    def blue(self, text, bright=False, reset=True):
        result = colorama.Fore.BLUE
        if bright:
            result += colorama.Style.BRIGHT
        result += text
        if reset:
            result += colorama.Style.RESET_ALL
        return result

    def yellow(self, text, bright=False, reset=True):
        result = colorama.Fore.YELLOW
        if bright:
            result += colorama.Style.BRIGHT
        result += text
        if reset:
            result += colorama.Style.RESET_ALL
        return result

    def green(self, text, bright=False, reset=True):
        result = colorama.Fore.GREEN
        if bright:
            result += colorama.Style.BRIGHT
        result += text
        if reset:
            result += colorama.Style.RESET_ALL
        return result

    def magenta(self, text, bright=False, reset=True):
        result = colorama.Fore.MAGENTA
        if bright:
            result += colorama.Style.BRIGHT
        result += text
        if reset:
            result += colorama.Style.RESET_ALL
        return result

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
