
import subprocess as sp

from .utils import MachopLogger


def flake(filepath):
    """
    pythonfiles can be a directory or file
    TODO: collect output from flake calls
    """
    log = MachopLogger('flake8')
    errformat = log.yellow("%(path)s ")
    errformat += "[" + log.magenta("%(row)s") + "]["
    errformat += log.magenta("%(col)s") + "]"
    errformat += log.red(" %(code)s ", True) + "%(text)s"
    cmdformat = ['--format', errformat]
    cmd = ['flake8']
    cmd.extend(cmdformat)
    cmd.append(filepath)
    proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = proc.communicate()
    exit = proc.returncode
    if exit != 0 and exit != 1:
        log.out('fatal error [%s]!' % exit)
    elif stderr != '':
        log.out('\n' + stderr)
    else:
        if stdout == '':
            msg = log.yellow("%s" % filepath) + ": "
            msg += log.green("no flake8 errors!", True)
            log.out(msg)
        path = None
        for line in stdout.split('\n'):
            newpath = line[:line.find('.py')]
            if path != newpath:
                if line != '' and path:
                    log.nl()
                path = newpath
            if line != '':
                log.out(line)
