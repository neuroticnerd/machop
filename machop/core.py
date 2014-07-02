
import os
import glob
import time

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

# @@@ WATCH_MAP will get very unwieldy in large projects, another solution
#     should be investigated for dispatching watch events
WATCH_MAP = {}
MACHOP_COMMANDS = {}
CURRENT_DIRECTORY = os.getcwd()


def default(defaultcommands):
    command('focus-energy', defaultcommands)


def command(cmdstring, cmdfunction):
    # @@@ TODO: validate command names before adding
    if not isinstance(cmdfunction, (list, tuple)):
        cmdfunction = [cmdfunction]
    MACHOP_COMMANDS[cmdstring] = cmdfunction


def run(command, *args, **kwargs):
    if not MACHOP_COMMANDS.get(command, None):
        print "%s is not a registered command!" % command
        return
    actions = MACHOP_COMMANDS[command]
    cmdpath = None
    if not isinstance(actions, (list, tuple)):
        actions = [actions]
    # @@@ determine if the action is a callable, or another command to run
    if 'cmdpath' not in kwargs.keys():
        cmdpath = CURRENT_DIRECTORY
    for action in actions:
        if not hasattr(action, '__call__'):
            if not cmdpath:
                run(action, *args, **kwargs)
            else:
                run(action, cmdpath, *args, **kwargs)
            continue
        result = None
        if cmdpath:
            result = action(cmdpath=cmdpath, *args, **kwargs)
            continue
        result = action(*args, **kwargs)
        if result:
            pass
    # @@@ raise exceptions for error results?


def watch(globpatterns, commandchain):
    """
    @@@ this NEEDS to be done using subprocess as an asynchronous task
    """

    class MachopHandler(PatternMatchingEventHandler):
        """ watcher for a file system event """
        def on_modified(self, event):
            if event.is_directory:
                return
            source = event.src_path
            if WATCH_MAP.get(source, None):
                for action in WATCH_MAP[source]:
                    run(action, cmdpath=source)

    if not isinstance(commandchain, (list, tuple)):
        commandchain = [commandchain]
    fileset = []
    if isinstance(globpatterns, (list, tuple)):
        for pattern in globpatterns:
            fileset.extend(glob.glob(pattern))
    else:
        glob.glob(globpatterns)
    for f in fileset:
        WATCH_MAP[os.path.join(CURRENT_DIRECTORY, f)] = commandchain
    handler = MachopHandler(patterns=globpatterns)
    observer = Observer()
    observer.schedule(handler, CURRENT_DIRECTORY, recursive=True)
    observer.start()
    print "now watching %s...\n" % globpatterns
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def leer(*args, **kwargs):
    pass

# make sure there's a default command in there
default(leer)
