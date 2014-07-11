
import time
import fnmatch
import hashlib

from .async import MachopAsyncCommand
from .utils import MachopLogger

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

    def __init__(self, globs=None, cmds=None, path=None):
        self.config(globs, cmds, path)
        self.log = None
        super(MachopWatchCommand, self).__init__()

    def config(self, patterns, commands, watchpath):
        self.globs = patterns if patterns else []
        self.actions = commands if commands else []
        self.watchpath = watchpath
        self.watching = True
        self.hashmap = {}

    def modified(self, eventsrc):
        if not self.has_changed(eventsrc):
            return
        for pattern in self.globs:
            if fnmatch.fnmatch(eventsrc, pattern):
                for action in self.actions:
                    action(cmdpath=eventsrc)
                break
        self.announce()

    def announce(self):
        log = self.log
        msg = "watching " + log.yellow + self.watchpath + log.reset
        for match in self.globs:
            msg += " for [" + log.yellow + match + log.reset + "]"
        msg += log.reset + "..."
        log.nl()
        log.out(msg)

    def run(self):
        self.log = MachopLogger('watch')
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

    def has_changed(self, key):
        hasher = hashlib.md5()
        with open(key, 'rb') as modfile:
            hasher.update(modfile.read())
        xhash = hasher.hexdigest()
        if self.hashmap.get(key, "") != xhash:
            self.hashmap[key] = xhash
            return True
        return False
