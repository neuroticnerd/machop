MACHOP
======


karatechop.py
-------------

The karatechop.py file tells machop what you want it to do and allows you to
write code for it to run, either automatically, or invoked manually. This file
should be in the root directory of the project you want to use machop for and
must be the current directory when invoking machop from the terminal.

Machop commands are simply python functions, the only real requirement is that
they accept ``**kwargs`` in their arguments since machop will pass in certain
keyword arguments for each call. Exceptions can occur if the command functions
do not at least accept ``**kwargs``. The only additional limitation is that
the command function must be top-level in karatechop.py; since machop is a
multiprocess application, functions which are not top-level cannot be seen
by certain parts of the machinery and will cause exceptions.

To access the machop API only a single import is needed::
    # example karatechop.py
    import machop

    def some_command(cmdpath, log, **kwargs):
        log.context("example.command")
        log.out("I'm a command, yay!")

    machop.command('example', some_command)

    """
    user$ machop example
    >> machop:example.command > I'm a command, yay!
    """

Certain arguments are always available to commands via ``**kwargs`` or directly
if referenced in the function definition:

``cmdpath``
    The path representing the context in which the command is executed;
    by default this is the current working directory, but for watch
    events it is the file or directory which triggered the event.

``log``
    A logging object which can be used to write text to the console. **Please**
    do **not** use ``print`` statements if you value your console output
    remaining unscrambled! Depending on the configuration of commands, machop
    is a concurrent application and ``print`` is neither thread, nor
    process-safe! The ``log`` parameter is both, but is not a normal
    ``logging.Logger`` object. Currently it does not support log levels and
    can only be written to using the ``log.out()`` method (see log section
    for full details).


machop API
----------

``machop.command(cmdstring, cmdfunction)``
    Commands are registered via ``machop.command()`` which takes a string
    name to identify the command (``cmdstring``) and a single command or list
    object of commands to be run (``cmdfunction``). Each element of (``cmdfunction``)
    **must** either be a callable object (e.g. functions) or the string name of
    another registered command.

``machop.default(defaultcommands)``
    This sets the default command(s) run when no command is specified in the
    terminal (e.g. ``user$ machop``). The ``defaultcommands`` parameter is
    either a single element or list object and like above, **must** contain
    only callable objects and string names of other registered commands.

``machop.watch(globpatterns, commandchain)``
    This uses watchdog for cross-platform file system monitoring, enabling
    machop commands to be executed in response to file modification. The
    ``globpatterns`` parameter should contain a list of glob-style patterns
    identifying files which should be responded to. ``commandchain`` follows the
    same rules as ``defaultcommands`` and ``cmdfunction``.
    *TODO: exclusion rules for ignoring events from files matching another set
    of patterns*

``machop.async(commands)``
    This starts a command running in its own separate process immediately. This
    should never be called outside of a command function (such as the default)
    because it can have unpredictable and potentially negative consequences
    such as infinite processes starting!

    Commands can be a single string or callable, a list of command strings or
    callables, or a dictionary object. If commands is a dict, each key in the
    dict is the context name of the command, and its value must be a single
    callable or command string::

        # example karatechop.py
        import machop

        def async1(log, **kwargs):
            log.out("async process 1")

        def async2(log, **kwargs):
            log.out("async process 2")

        def base(log, **kwargs):
            machop.async({'proc.1': async1, 'proc.2': async2})

        machop.default(base)

``machop.shell(command, realtime=None, cblog=None, shell=True)``
    This immediately executes a shell command in a subprocess, blocking the
    calling process until it terminates or causes an exception. As with async,
    it should not be called outside of command functions as it can cause
    unpredictable problems.

    ``command`` is a string that is the command to be executed, or a list if the
    command has parameters, with the first element of the list being the actual
    command to be invoked.

    ``realtime`` if set to True will log stdout of the shell command to the
    terminal as it happens as opposed to waiting for the process to conclude;
    alternatively this can be set to a callback function which accepts one
    parameter which when called will be a single line of output from stdout.

    ``cblog`` can be set to a log object which will override the log to use if
    ``realtime`` is set to anything aside from ``None``. If cblog is used in
    conjunction with ``realtime`` then the callback function must also accept a
    second parameter which will be this log::

        def python_test(cmdpath, log, **kwargs):
            # since the line handler is defined within the scope of this
            # command it could use the 'log' parameter of the command, but it
            # accepts the second parameter simply to show the use of
            # the cblog parameter in a shell() call
            def rthandler(line, log):
                log.out(line, False)

            log.context('py.test')
            log.out('testing %s...' % log.yellow(cmdpath))
            res = machop.shell(['py.test', '--cov'], realtime=rthandler, cblog=log)
            if res.exit:
                log.out(log.red("process error", True) + ":\n" + res.stderr.strip())
            log.nl()
            return True if not res.exit else False

    The return value of ``machop.shell()`` is a ``ShellResult`` object containing
    data on the process:

    ``class ShellResult(object)``

        ``proc``: The actual process object as returned by subprocess.Popen
        
        ``stdout``: The stdout data for the process. If no realtime logging was
        performed then this will contain the output of the shell process. If
        realtime logging was done, then it will likely be empty.
        
        ``stderr``: This contains stderr output for the process and is only
        available after the process ends or fails. Note that some applications
        just print stderr information to stdout.
        
        ``exit``: This is a shortcut for accessing the return code for the
        shell process, which can also be accessed through ``obj.proc.returncode``


log parameter
-------------

The ``log`` parameter has three core methods available to the commands:

``out(message, noformat=False)``
    This is fairly self-explanatory, ``message`` is what you would like written
    to the console, and noformat determines whether that output should be
    prefaced by contextual information. The contextual information may not be
    useful for many writes of small lines, but if it is, consider aggregating
    the lines into a single larger ``out`` call::

        # example

        log.out("application is running a command!")
        # >> machop:command > application is running a command!

        log.out("application is running a command!", True)
        # >> application is running a command!

``nl()``
    This is simply a shortcut for outputing a newline to the console and
    inherently uses ``noformat=True`` to avoid empty formatted lines.

``context(newcontext=None)``
    If ``newcontext`` is supplied, then it will change the formatting context of
    calls to that logging object, and regardless will return the current
    context of that logging object. If ``newcontext`` was supplied, it will
    return the **previous** context::

        log.out("application is running a command!")
        # >> machop:command > application is running a command!

        oldcontext = log.context("new-context")
        log.out(oldcontext)
        # >> machop:new-context > command

The logging object also has some built-in class methods for wrapping text in
ANSI formatting for colored output to the terminal. colorama is used to ensure
the coloring works on Windows systems, but be aware that currently, output
from shell or subprocesses started by machop cannot be captured with ANSI
formatting and additionally depends on how the given tool was coded.
*currently there is no way to disable ANSI formatting manually in machop, but
its on my todo list!*

``red(text, bright=False, reset=True)``

``cyan(text, bright=False, reset=True)``

``blue(text, bright=False, reset=True)``

``yellow(text, bright=False, reset=True)``

``green(text, bright=False, reset=True)``

``magenta(text, bright=False, reset=True)``
    
    ``text``: simply the string you want encased in ANSI escapes
    
    ``bright``: use True if you desire bright text for that color
    
    ``reset``: use False to forego resetting ANSI formatting
