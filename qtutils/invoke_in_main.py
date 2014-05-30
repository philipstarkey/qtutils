#####################################################################
#                                                                   #
# invoke_in_main.py                                                 #
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

import sys
import Queue
import threading
import functools

if 'PySide' in sys.modules.copy():
    from PySide.QtCore import *
else:
    from PyQt4.QtCore import *


class CallEvent(QEvent):
    """An event containing a request for a function call."""
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self, queue, exceptions_in_main, fn, *args, **kwargs):
        QEvent.__init__(self, self.EVENT_TYPE)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self._returnval = queue
        # Whether to raise exceptions in the main thread or store them
        # for raising in the calling thread:
        self._exceptions_in_main = exceptions_in_main
    

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
    QCoreApplication.postEvent(caller, CallEvent(queue, exceptions_in_main, fn, *args, **kwargs))
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
    
    
if __name__ == '__main__':   
    import signal
    
    def loop(index):
        if index < 3:
            thread = inthread(loop, index+1)
        while True:
            # print 'MyThread-%d: %s'%(index,str(QThread.currentThread()))
            # print 'MyThread-%d: %s'%(index,threading.current_thread().name)
            #another_function(index)
            inmain(myFunction,index)
    
    def another_function(index):
        print 'in thread-%d, running in thread: %s'%(index,threading.currentThread().name)
    
    def myFunction(index):
        print 'from thread-%d, running in thread: %s'%(index,threading.currentThread().name)
        pass
        
    def myFunction2():
        print 'from MainThread, running in thread: %s'%(threading.currentThread().name)
        QTimer.singleShot(0,x)

    qapplication = QCoreApplication(sys.argv)
    def sigint_handler(*args):
        qapplication.quit()
      
    signal.signal(signal.SIGINT, sigint_handler)

    thread = inthread(loop, 1)
    x = lambda: inmain(myFunction2)
    timer = QTimer.singleShot(0,x)
    qapplication.exec_()

