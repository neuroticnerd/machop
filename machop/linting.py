
from .utils import MachopLogger, ensure_list

from subprocess import call


def flake(pythonfiles):
    """
    pythonfiles can be a directory, file, or list/tuple of files
    TODO: collect output from flake calls
    """
    log = MachopLogger('flake')
    fileset = ensure_list(pythonfiles)
    error = False
    for f in fileset:
        msg = "linting " + log.yellow + "%s" % f + log.reset + "..."
        log.out(msg)
        result = call(['flake8', f], shell=True)
        if result != 0:
            error = True
        else:
            msg = " " + log.yellow + "%s" % f + log.reset
            msg += ": " + log.green_br + "no flake8 errors!" + log.reset
            log.out(msg)
        log.out("\n", noformat=True)
    if not error:
        pass
