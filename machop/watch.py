
import time
import fnmatch

from .async import MachopAsyncCommand
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class MachopWatchCommand(MachopAsyncCommand):

    class MachopHandler(PatternMatchingEventHandler):
        """ watcher for a file system event """
        def on_modified(self, event):
            if event.is_directory:
                return
            source = event.src_path
            self._watcher.modified(source)

    def __init__(self, globs=None, cmds=None, path=None, runner=None):
        self.config(globs, cmds, path)
        self.run_command = runner
        super(MachopWatchCommand, self).__init__()

    def config(self, patterns, commands, watchpath):
        self.globs = patterns if patterns else []
        self.actions = commands if commands else []
        self.watchpath = watchpath
        self.watching = True

    def modified(self, eventsrc):
        match = False
        for pattern in self.globs:
            if fnmatch.fnmatch(eventsrc, pattern):
                match = True
        if not match:
            return
        for action in self.actions:
            self.run_command(action, cmdpath=eventsrc)
        self.announce()

    def announce(self):
        print "\nnow watching %s..." % self.globs

    def run(self):
        handler = self.MachopHandler(patterns=self.globs)
        handler._watcher = self
        self.observer = Observer()
        self.observer.schedule(handler, self.watchpath, recursive=True)
        self.observer.start()
        self.announce()
        while self.watching:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
        self.observer.stop()
        self.observer.join()

    def shutdown(self):
        self.wait = False
