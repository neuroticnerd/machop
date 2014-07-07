"""
@@@ command dependencies
@@@ concurrency for async commands
@@@ use logging module instead of print

decorators for adding specific parameters
functions define jobs

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

integrate flake8 and pytest/coverage into machop core

??? use signals for triggering watch events? (blinker, pydispatcher, pysignals)
"""
from version import __version__
from core import default, command, run, watch
from linting import flake
