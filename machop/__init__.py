"""
@@@ make command structures into classes
@@@ support command chain order dependencies
@@@ concurrency for multiple async commands
@@@ use logging module instead of print
@@@ colored console output
@@@ integrate flake8 and pytest/coverage into machop core
@@@ decorators for adding specific static parameters
@@@ use signals for triggering watch events? (blinker, pydispatcher, pysignals)
@@@ use argparse in future for better cli arg handling
@@@ separate logic out of __main__.py into other files, then import

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
"""
from version import __version__
from core import default, command, run, watch
from linting import flake
