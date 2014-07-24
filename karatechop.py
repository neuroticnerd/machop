
import machop
import os


def line_handler(line, log):
    output = log.cyan(log.context()) + "."
    if line.stream == 'stderr':
        output += log.red(line.stream, False) + " > "
    elif line.stream == 'stdout':
        output += log.green(line.stream, False) + " > "
    else:
        output += line.stream + " > "
    output += line.line
    log.out(output, noformat=True)


def python_test(cmdpath, log, **kwargs):
    log.context('py.test')
    log.out('testing %s...' % log.yellow(cmdpath))
    res = machop.shell(
        ['py.test', '--cov', os.path.dirname(cmdpath)],
        rthandler=line_handler, rtlog=log)
    if res.exit:
        log.out(log.red("process error", True) + ":\n" + res.stderr.strip())
    log.nl()
    return True if not res.exit else False


@machop.kwargs(url='www.google.com')
def pingthing(log, url, **kwargs):
    log.context('ping')
    log.out('pinging %s' % log.yellow(url))
    res = machop.shell(
        ['ping', url], rthandler=line_handler, rtlog=log)
    log.nl()
    return True if not res.exit else False


def foresight(**kwargs):
    machop.watch('*.py', ['flake', 'pytest'])
    machop.async({'py.test': 'pytest', 'ping': pingthing})


machop.command('pytest', python_test)
machop.command('watch', ['flake', foresight])
machop.default('watch')
