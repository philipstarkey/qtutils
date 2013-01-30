import Queue
import threading
import functools
import inspect

from PySide.QtCore import *

from locking import qtlock

class CallEvent(QEvent):
    """An event containing a request for a function call."""
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self, fn, *args, **kwargs):
        QEvent.__init__(self, self.EVENT_TYPE)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.done = False
        self._returnval = Queue.Queue()
        self._lock = threading.Lock()
        self._exc_info = None
        self.cancelled = False
        
    def wait(self):
        if qtlock.held():
            message = ('Deadlock: Either you are already in the main thread or you have acquired the qtlock. ' +
                       'Either way the qt mainloop is blocked and the function you are waiting on will never run')
            raise threading.ThreadError(message)
        result = self._returnval.get()
        if self._exc_info is not None:
            # If there was an exception, raise it:
            type, value, traceback = self.exc_info
            raise type, value, traceback
        return result
    
    def cancel(self):
        with self._lock:
            if self.done:
                return False
            self.cancelled = True
            return True
                
                
class Caller(QObject):
    """An event handler which calls the function held within a CallEvent."""
    def event(self, event):
        with event._lock:
            if not event.cancelled:
                try:
                    result = event.fn(*event.args, **event.kwargs)
                except Exception:
                    # Will re-raise the exception in the calling thread:
                    event._exc_info = sys.exc_info()
                    result = None
                event._returnval.put(result)
                event.done = True
        return True
        
caller = Caller()


def inmain(fn, *args, **kwargs):
    """Execute a function in the main thread. Wait for it to complete
    and return its return value."""
    if threading.current_thread().name == 'MainThread':
        return fn(*args, **kwargs)
    event = CallEvent(fn, *args, **kwargs)
    QCoreApplication.postEvent(caller, event)
    return event.wait()
    
def inmain_later(fn, *args, **kwargs):
    """Asks the mainloop to call a function when it has time. Immediately
    returns the event that was sent to the mainloop.  Functions are
    guaranteed to be called in the order they were requested."""
    event = CallEvent(fn, *args, **kwargs)
    QCoreApplication.postEvent(caller, event)
    return event

def inthread(f,*args,**kwargs):
    thread = threading.Thread(target=f, args=args, kwargs=kwargs)
    thread.daemon=True
    thread.start()
    
def inmain_decorator(wait_for_return=True):
    def wrap(fn):
        """A decorator which sets any function to always run in the main thread."""
        @functools.wraps(fn)
        def f(*args,**kwargs):
            if wait_for_return:
                return inmain(fn, *args, **kwargs)
            return inmain_later(fn, *args, **kwargs)  
        return f
    return wrap
    
