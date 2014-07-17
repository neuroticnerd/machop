
import machop


def rthandler(line, log):
    log.out(line, False)


def python_test(cmdpath, log, **kwargs):
    log.context('py.test')
    log.out('testing %s...' % log.yellow(cmdpath))
    res = machop.shell(['py.test', '--cov'], realtime=rthandler, cblog=log)
    if res.exit:
        log.out(log.red("process error", True) + ":\n" + res.stderr.strip())
    log.nl()
    return True if not res.exit else False


def pingthing(log, **kwargs):
    log.context('ping')
    log.out('pinging %s' % log.yellow('google.com'))
    res = machop.shell(['ping', 'google.com'], realtime=rthandler, cblog=log)
    log.nl()
    return True if not res.exit else False


def foresight(**kwargs):
    machop.watch('*.py', ['flake', 'pytest'])
    machop.async({'py.test': 'pytest', 'ping': pingthing})


machop.command('pytest', python_test)
machop.command('watch', ['flake', foresight])
machop.default('watch')
