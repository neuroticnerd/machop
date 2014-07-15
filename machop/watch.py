
import time
import fnmatch
import hashlib

from .async import MachopAsyncCommand
from .mplog import MachopLog
from .linting import _set_flake_q

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
        self.queue = None
        super(MachopWatchCommand, self).__init__(None, None, None)

    def config(self, patterns, commands, watchpath):
        self.globs = patterns if patterns else []
        self.actions = commands if commands else []
        self.watchpath = watchpath
        self.watching = True
        self.hashmap = {}

    def set_queue(self, queue):
        self.queue = queue

    def modified(self, eventsrc):
        if not self.has_changed(eventsrc):
            return
        for pattern in self.globs:
            if fnmatch.fnmatch(eventsrc, pattern):
                for action in self.actions:
                    action(cmdpath=eventsrc, log=self.log)
                break
        self.announce()

    def announce(self, nl=False):
        log = self.log
        msg = "watching " + log.yellow(self.watchpath)
        for match in self.globs:
            msg += " for [" + log.yellow(match) + "]"
        msg += "..."
        if nl:
            msg += '\n'
        log.out(msg)

    def run(self):
        self.log = MachopLog(self.queue, 'watch')
        _set_flake_q(self.queue)
        handler = self.MachopHandler(patterns=self.globs)
        handler._watcher = self
        self.observer = Observer()
        self.observer.schedule(handler, self.watchpath, recursive=True)
        self.observer.start()
        self.announce(True)
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
