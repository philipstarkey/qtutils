import sys
import Queue
import threading
import functools

from PySide.QtCore import *

class CallEvent(QEvent):
    """An event containing a request for a function call."""
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self, queue, fn, *args, **kwargs):
        QEvent.__init__(self, self.EVENT_TYPE)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self._returnval = queue
        # Whether to raise exceptions in the main thread or store them
        # for raising in the calling thread:
        self._exceptions_in_main = True
    

class Caller(QObject):
    """An event handler which calls the function held within a CallEvent."""
    def event(self, event):
        event.accept()
        exception = None
        try:
            result = event.fn(*event.args, **event.kwargs)
        except Exception:
            # Store for re-raising the exception in the calling thread:
            exception = sys.exc_info()
            result = None
            if event._exceptions_in_main:
                # Or, if nobody is listening for this exception,
                # better raise it here so it doesn't pass
                # silently:
                raise
        finally:
            event._returnval.put([result,exception])  
        return True
         
caller = Caller()

def inmain(fn, *args, **kwargs):
    """Execute a function in the main thread. Wait for it to complete
    and return its return value."""
    if threading.current_thread().name == 'MainThread':
        return fn(*args, **kwargs)
    return get_inmain_result(in_main_later(fn,False,*args,**kwargs))
    
def inmain_later(fn, *args, **kwargs):
    return in_main_later(fn,True,*args,**kwargs)
    
def in_main_later(fn, exceptions_in_main, *args, **kwargs):
    """Asks the mainloop to call a function when it has time. Immediately
    returns the queue that was sent to the mainloop.  A call to queue.get()
    will return a list of [result,exception] where exception=[type,value,traceback]
    of the exception.  Functions are guaranteed to be called in the order
    they were requested."""        
    queue = Queue.Queue()
    event = CallEvent(queue, fn, *args, **kwargs)
    event._exceptions_in_main = exceptions_in_main
    QCoreApplication.postEvent(caller, event)
    return queue
    
def get_inmain_result(queue):
    result,exception = queue.get()
    if exception is not None:
        type, value, traceback = exception
        raise type, value, traceback
    return result

def inthread(f,*args,**kwargs):
    thread = threading.Thread(target=f, args=args, kwargs=kwargs)
    thread.daemon=True
    thread.start()
    return thread
    
def inmain_decorator(wait_for_return=True,exceptions_in_main=True):
    """ A decorator which sets any function to always run in the main thread
    If wait_for_return=True, then exceptions_in_main is ignored.
    """
    def wrap(fn):
        """A decorator which sets any function to always run in the main thread."""
        @functools.wraps(fn)
        def f(*args,**kwargs):
            if wait_for_return:
                return inmain(fn, *args, **kwargs)
            return in_main_later(fn, exceptions_in_main, *args, **kwargs)  
        return f
    return wrap
    
