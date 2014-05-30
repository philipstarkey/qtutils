#####################################################################
#                                                                   #
# locking.py                                                        #
#                                                                   #
# Copyright 2013, Christopher Billington, Philip Starkey            #
#                                                                   #
# This file is part of the qtutils project                          #
# (see https://bitbucket.org/philipstarkey/qtutils )                #
# and is licensed under the 2-clause, or 3-clause, BSD License.     #
# See the license.txt file in the root of the project               #
# for the full license.                                             #
#                                                                   #
#####################################################################

import threading
import sys

if 'PySide' in sys.modules.copy():
    from PySide.QtCore import *
else:
    from PyQt4.QtCore import *

class BlockEvent(QEvent):
    """An event requesting the mainloop to be blocked until further notice."""
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self, blocked, unblock):
        QEvent.__init__(self, self.EVENT_TYPE)
        self.blocked = blocked
        self.unblock = unblock
    
class Blocker(QObject):
    """An event handler which blocks until event.unblock is set."""
    def event(self, event):
        event.blocked.set()
        event.unblock.wait()
        event.unblock.clear()
        return True
        
blocker = Blocker()
        
class QtLock():
    """A context manager which ensures that the Qt mainloop is doing
    nothing. It does this by invoking a function call in the main thread
    which simply blocks. Entering the context manager will block until
    the main loop can be blocked, and exiting the context manager will
    unblock the mainloop. If we are already in the main thread, the
    context manager does nothing. Regardless of thread, it can be used
    re-entrantly and is completely thread-safe."""
    def __init__(self):
        # Thread local storage, to make our methods thread-safe without
        # locking:
        self.local = threading.local()

    def per_thread_init(self):
        """Due to thread local storage, we couldn't initialise in __init__
        for all threads. Each time a new thread is encountered by a
        method, we create thread local attributes for it."""
        if threading.current_thread().name == 'MainThread':
            # The main thread does not need to block itself:
            self.local.held = 1
        else:
            # Other threads will need to coordinate blocking the mainloop
            # with threading.Event()s:
            self.local.held = 0  
            self.local.blocked = threading.Event()
            self.local.unblock = threading.Event()
    
    def held(self):
        if not hasattr(self.local,'held'):
            self.per_thread_init()
        return self.local.held
                
    def enforce(self, enable=True):
        """Raises an exception when Qt method calls are made from a
        non-main thread without the mainloop blocked. Only takes effect
        on threads created after enforce() is called."""
        def enforce(frame, event, func):
            if event == 'c_call':
                if isinstance(func.__self__, QObject):
                    if not self.held():
                        message = 'qtlock was not acquired for this Qt call, and we are not in the main thread.'
                        raise threading.ThreadError(message)
        threading.setprofile(enforce if enable else None)
    
    def __enter__(self):
        # Only block the mainloop if it is not already blocked:
        if not self.held():
            # Ask the mainloop to please process a BlockEvent when it gets the chance:
            event = BlockEvent(self.local.blocked, self.local.unblock)
            QCoreApplication.postEvent(blocker, event)
            # Wait until the mainloop is blocked:
            self.local.blocked.wait()
            self.local.blocked.clear()
        # Keep track of the re-entrance depth:
        self.local.held += 1
                    
    def __exit__(self,*args):
        # Only unblock the mainloop if we've popped out of the outer-most
        # context:
        self.local.held -= 1
        if not self.local.held:
            self.local.unblock.set()

qtlock = QtLock()
