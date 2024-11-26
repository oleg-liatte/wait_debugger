import sys
import os
import time
import threading

from importlib.abc import MetaPathFinder
from typing import Optional, Callable

hasDebugger = False
hasDebuggerCondition = threading.Condition()


class NotificationFinder(MetaPathFinder):
    def find_spec(self, fullname, _path, _target=None):
        global hasDebugger
        if 'pydevd' in fullname:
            with hasDebuggerCondition:
                hasDebugger = True
                hasDebuggerCondition.notify()


sys.meta_path.insert(0, NotificationFinder())


def wait_debugger(pred: Optional[Callable[[], bool]] = None):
    if pred is not None and not pred():
        return

    hadDebugger = hasDebugger

    if not hadDebugger:
        print(f'Waiting for debugger to attach to pid {os.getpid()}...')

    with hasDebuggerCondition:
        while not hasDebugger:
            hasDebuggerCondition.wait()

    if not hadDebugger:
        print('Attached! Waiting 5 seconds before continuing...')
        time.sleep(5)  # Give the debugger some time to attach
        return
