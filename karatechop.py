"""
machop commands are simply python functions, the only requirement is that
they accept **kwargs in their arguments since machop will pass in certain
keyword arguments for each execution.

commands are registered via the machop.command() function which takes a string
name to identify the command and a callable, or list of callables to be run.

machop.default() creates a command or list of commands that are run when no
arguments are given on the command line (e.g. 'machop').

certain arguments are always available to commands via **kwargs or directly if
reference in the function definition:
- cmdpath = the path or directory in the context the command is to be executed,
            by default this is the current working directory, but for watch
            events it is the file or directory which triggered the change.
"""
import machop 


def python_lint(cmdpath, **kwargs):
    machop.flake(cmdpath)


def python_test(**kwargs):
    print "this is the python testing command"


def python_cov(**kwargs):
    print "this is the python coverage command"


def focus_energy(**kwargs):
    machop.watch(['*.py', '*/*.py'], ['flake'])  # , 'pytest', 'coverage'])

machop.command('flake', python_lint)
machop.command('pytest', python_test)
machop.command('coverage', python_cov)
machop.command('pycheck', ['flake', 'pytest', 'coverage'])
machop.command('watch', focus_energy)
machop.default('watch')
