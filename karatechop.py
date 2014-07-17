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


def python_lint(cmdpath, **kwargs):
    machop.flake(cmdpath)


def python_test(cmdpath, log, **kwargs):
    log.context('py.test')

    def linehandler(line, stream):
        if line == '':
            log.out("EMPTYLINE")
        log.out(line, True)

    log.out('testing %s...' % log.yellow(cmdpath))
    result = machop.shell(['py.test'], realtime=linehandler)
    log.nl()
    return True if not result[0] else False


def foresight(**kwargs):
    machop.watch('*.py', ['flake', 'pytest'])
    machop.async({'py.test': python_test})


machop.command('flake', python_lint)
machop.command('pytest', python_test)
machop.command('watch', ['flake', foresight])
machop.default('watch')
