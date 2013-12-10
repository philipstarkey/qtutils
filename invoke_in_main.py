import sys
import Queue
import threading
import functools

from PySide.QtCore import *

def run_function(tup):
    queue, exceptions_in_main, fn, args, kwargs = tup
    exception = None
    try:
        result = fn(*args, **kwargs)
    except Exception:
        # Store for re-raising the exception in the calling thread:
        exception = sys.exc_info()
        result = None
        if exceptions_in_main:
            # Or, if nobody is listening for this exception,
            # better raise it here so it doesn't pass
            # silently:
            raise
    finally:
        queue.put([result,exception])  
        
class Caller(QObject):        
    main_thread_posting_event = Signal(tuple)
    def __init__(self,*args,**kwargs):
        QObject.__init__(self,*args,**kwargs)
        self.main_thread_posting_event.connect(run_function)

caller = Caller()
        
def inthread(f, *args, **kwargs):
    thread = threading.Thread(target=f, args=args, kwargs=kwargs)
    thread.daemon=True
    thread.start()
    return thread

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
    
    if threading.current_thread().name == 'MainThread':
        caller.main_thread_posting_event.emit((queue, exceptions_in_main, fn, args, kwargs))
    else:
        qt_thread_queue.put((queue, exceptions_in_main, fn, args, kwargs))
    return queue
  
def get_inmain_result(queue):
    result,exception = queue.get()
    if exception is not None:
        type, value, traceback = exception
        raise type, value, traceback
    return result

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
 
    
class EventPostingThread(QThread):
    postingEvent = Signal(tuple)
    def __init__(self, queue, parent = None):
        """
        Must be instantiated in the main thread or the target function of another
        instance of this class
        
        An exception will be raised if instantiated from a plain Python thread or 
        a standard QThread.
        """
        # runs in the thread in which the thread is instantiated        
        QThread.__init__(self,parent)
        self.queue = queue
        # If created in the main thread, this is just run in the main thread
        # If created in another instance of this class, then inmain will
        #    use that threads postingEvent signal to run the code in the main thread
        inmain(self.postingEvent.connect,run_function)

    def run(self):
        while True:
            tup = self.queue.get()
            self.postingEvent.emit(tup)
     
qt_thread_queue = Queue.Queue()
qt_thread = EventPostingThread(qt_thread_queue)
qt_thread.start()

    
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

