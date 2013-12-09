import sys
import Queue
import threading
import functools

from PySide.QtCore import *

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

def post_event(tup):
    queue, exceptions_in_main, fn, args, kwargs = tup
    event = CallEvent(queue, exceptions_in_main, fn, *args, **kwargs)
    QCoreApplication.postEvent(caller,event)

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
        post_event((queue, exceptions_in_main, fn, args, kwargs))
    else:
        try:
            qthread = QThread.currentThread()
            qthread.postingEvent.emit((queue, exceptions_in_main, fn, args, kwargs))
        except Exception:
            raise RuntimeError('You can only call the inmain and inmain_later functions, or a function decorated with the inmain_decorator, from an InMainThread or the main thread.')
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
    
def in_qt_thread(target, parent = None, args = (), kwargs = {}):
    thread = EventPostingThread(target, parent, args, kwargs)
    thread.start()
    return thread
    
class EventPostingThread(QThread):
    postingEvent = Signal(tuple)
    def __init__(self, target, parent = None, args = (), kwargs = {}):
        """
        Must be instantiated in the main thread or the target function of another
        instance of this class
        
        An exception will be raised if instantiated from a plain Python thread or 
        a standard QThread.
        """
        # runs in the thread in which the thread is instantiated        
        QThread.__init__(self,parent)
        self.func = target
        self.args = args
        self.kwargs = kwargs
        # If created in the main thread, this is just run in the main thread
        # If created in another instance of this class, then inmain will
        #    use that threads postingEvent signal to run the code in the main thread
        inmain(self.postingEvent.connect,post_event)

###
# Deamon threads code commented out because I can't seem to make a NON-daemon QThread
###
        # # configure default value of daemon property
        # self._daemon_thread = False        
        # try:
            # qthread = QThread.currentThread()
            # if isinstance(qthread,InMainThread):
                # self.daemon = qthread.daemon
        # except Exception:
            # pass
        
    # @property
    # def daemon(self):
        # return self._daemon_thread
    
    # # Daemon property. If a thread is a daemon thread, it should be force terminated when the 
    # # eventloop in the main thread exits 
    # @daemon.setter
    # def daemon(self,value):
        # if self.isRunning():
            # raise RuntimeError('You cannot change the daemon property of this thread after it has been started')
        # value = bool(value)
        # self._daemon_thread = value
        # if self.daemon:
            # print 'setting daemon True'
            # # connect finished signal
            # self.finished.connect(self.onFinished)
            # # Connect about to Quit signal
            # QCoreApplication.instance().aboutToQuit.connect(self.terminate)
    
    # def onFinished(self):
        # print 'thread finished'
        # QCoreApplication.instance().aboutToQuit.disconnect(self.terminate)
        
    def run(self):
        self.func(*self.args,**self.kwargs)
    
    # convenience function to simulate python thread
    def is_alive(self):
        return self.isRunning()
        
    # convenience function to simulate Python thread
    def join(self,timeout=None):
        if timeout is None:
            return self.wait()
        else:
            return self.wait(timeout*1000)
    
    
if __name__ == '__main__':   
    import signal
    
    def loop(index):
        if index < 3:
            thread = in_qt_thread(target=loop,args=(index+1,))
        while True:
            # print 'MyThread-%d: %s'%(index,str(QThread.currentThread()))
            # print 'MyThread-%d: %s'%(index,threading.current_thread().name)
            another_function(index)
            inmain(myFunction,index)
    
    def another_function(index):
        print 'in thread-%d, running in thread: %s'%(index,threading.currentThread().name)
    
    def myFunction(index):
        print 'from thread-%d, running in thread: %s'%(index,threading.currentThread().name)
        pass

    qapplication = QCoreApplication(sys.argv)
    def sigint_handler(*args):
        qapplication.quit()
      
    signal.signal(signal.SIGINT, sigint_handler)

    thread = in_qt_thread(target=loop, args=(1,))
    
    qapplication.exec_()

