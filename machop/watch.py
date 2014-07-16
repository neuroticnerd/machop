
import fnmatch
import hashlib

from .mplog import MachopLog
from .utils import MachopProcess, wait_for_interrupt

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class MachopWatchCommand(MachopProcess):

    class MachopHandler(PatternMatchingEventHandler):
        """ watcher for a file system event """
        def on_modified(self, event):
            if event.is_directory:
                return
            source = event.src_path
            self._watcher.modified(source)

    def __init__(self, globs=None, cmds=None, path=None, queue=None):
        super(MachopWatchCommand, self).__init__()
        recreate = (globs, cmds, path, queue)
        self._safe_process(queue=queue, cfgpath=path, init=recreate)
        self.globs = globs if globs else []
        self.actions = cmds if cmds else []
        self.watchpath = path
        self.queue = queue
        self.hashmap = {}
        self.log = None

    def set_queue(self, queue):
        self.queue = queue

    def modified(self, eventsrc):
        """
        @@@ needs proper event handling for actions!!!
        """
        if not self.has_changed(eventsrc):
            return
        matched = False
        for pattern in self.globs:
            if fnmatch.fnmatch(eventsrc, pattern):
                matched = True
                break
        if matched:
            for action in self.actions:
                action(cmdpath=eventsrc, log=MachopLog(self.queue, 'watch'))
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
        self.handler = self.MachopHandler(patterns=self.globs)
        self.handler._watcher = self
        self.observer = Observer()
        self.observer.schedule(self.handler, self.watchpath, recursive=True)
        self.observer.start()
        self.announce(True)
        wait_for_interrupt(self.observer)
        self.observer.stop()
        self.observer.join(3)

    def has_changed(self, key):
        hasher = hashlib.md5()
        with open(key, 'rb') as modfile:
            hasher.update(modfile.read())
        xhash = hasher.hexdigest()
        if self.hashmap.get(key, "") != xhash:
            self.hashmap[key] = xhash
            return True
        return False
