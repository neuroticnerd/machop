"""
machop commands are simply python functions, the only requirement is that
they accept **kwargs in their arguments since machop will pass in certain
keyword arguments for each execution.

commands are registered via the machop.command() function which takes a string
name to identify the command and a callable, or list of callables to be run.

machop.default() creates a command or list of commands that are run when no
arguments are given on the command line (e.g. 'machop').

certain arguments are always available to commands via **kwargs or directly if
referenced in the function definition:
- cmdpath = the path or directory in the context the command is to be executed,
            by default this is the current working directory, but for watch
            events it is the file or directory which triggered the change.
- log = a custom logging object which contains a 'out' method to send text
        to the console. this logger uses a multiprocess Queue to achieve thread
        and multiprocess safety.
"""
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
