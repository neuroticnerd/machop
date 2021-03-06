"""
@@@ pipe commands into input of another
@@@ simple support for plugins
@@@ polling module to execute some task at a designated interval
@@@ glob input to map command to set of files
@@@ command queue with worker processes
@@@ commands are classes with __call__
@@@ allow passing arguments to commands
@@@ daemon process to handle management while main process remains unblocked
@@@ timestamp log entries for chronological order - multiprocess priority queue
@@@ look into using pty or equivalent for colored child output
@@@ allow additional importing within karatechop.py of other files
@@@ fix unbuffered to skip always having at least a single blank line
@@@ correct exception handling for child processes
@@@ use events to softly kill child processes & threads
@@@ reload commands when karatechop.py changes
@@@ full recursion for _get_callables to traverse command aliases
@@@ ability to direct the output of machop (e.g. to a file)
@@@ use MachopException for within these modules
@@@ manual sync by queueing shell commands to redirect actual output to console
@@@ debug mode which outputs full stack traces
@@@ turn color on/off at will
@@@ allow console input while running bulk of application in another process
@@@ better way to determine correct calls to colorama init()
@@@ global hashing mechanism to determine if a command needs to be run
@@@ make command structures into classes
@@@ support command chain order dependencies
@@@ concurrency for multiple async commands
@@@ --path argument to manually set the current directory
@@@ --karatechop argument to manually specify the location of config
@@@ alternative way of defining built-in commands
@@@ proper error + exception handling for commands and processes
@@@ use logging queue for multiprocess logging
@@@ colored console output
@@@ integrate flake8 and pytest/coverage into machop core
@@@ decorators for adding specific static parameters
@@@ use signals for triggering watch events? (blinker, pydispatcher, pysignals)
@@@ use argparse in future for better cli arg handling
@@@ separate logic out of __main__.py into other files, then import
@@@ 'machop init' command to create a karatechop.py file


machop.config
machop.parameters
machop.load
machop.shell
machop.job (task)
machop.watch (w/exclude + include directives)
machop.event (signals?)
machop.queue
machop.concurrent (async)
machop.default
machop.log
machop.run (for tasks or processes?)
machop.alias (associate command with series of commands)

https://bitbucket.org/schettino72/doit/src/a55aa33b6807?at=default
"""
from .version import __version__
from .api import default, command, run, async, watch, shell
from .linting import flake
from .decorators import kwargs

__all__ = [
    '__version__', 'default', 'command',
    'run', 'async', 'watch', 'shell', 'flake', 'kwargs'
    ]
