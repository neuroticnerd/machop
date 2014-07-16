"""
@@@ async processes use unbuffered output
@@@ correct exception handling for child processes
@@@ use events to softly kill child processes & threads
@@@ reload when karatechop.py changes
@@@ ability to direct the output of machop (e.g. to a file)
@@@ use MachopException for within these modules
@@@ debug mode which outputs full stack traces
@@@ turn color on/off at will
@@@ better way to determine correct calls to colorama init()
@@@ global hashing mechanism to determine if a command needs to be run
@@@ make command structures into classes
@@@ support command chain order dependencies
@@@ concurrency for multiple async commands
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

__all__ = [
    '__version__', 'default', 'command',
    'run', 'async', 'watch', 'shell', 'flake'
    ]
