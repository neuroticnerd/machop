
import subprocess as sp

from .mplog import MachopLog

_flake_q = None


def _set_flake_q(queue):
    global _flake_q
    _flake_q = queue


def flake(filepath):
    """
    pythonfiles can be a directory or file
    TODO: collect output from flake calls
    """
    if not _flake_q:
        raise ValueError("log queue is not configured!")
    log = MachopLog(_flake_q, 'flake8')
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
            msg = log.green("no lint found!", True)
            msg += log.yellow("\n %s\n" % filepath)
            log.out(msg)
        else:
            path = None
            output = log.red("lint found!", True)
            for line in stdout.split('\n'):
                newpath = line[:line.find('.py')]
                if path != newpath:
                    if line != '' and path:
                        output += '\n'
                    path = newpath
                if line != '':
                    output += '\n ' + line
            output += '\n'
            log.out(output)
