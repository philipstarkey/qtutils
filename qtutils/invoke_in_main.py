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

from __future__ import division, unicode_literals, print_function, absolute_import
import sys
PY2 = sys.version_info[0] == 2
if PY2:
    str = unicode
    from Queue import Queue
else:
    from queue import Queue

import threading
import functools

from qtutils.qt.QtCore import QEvent, QObject, QCoreApplication, QTimer, QThread


def _reraise(exc_info):
    type, value, traceback = exc_info
    # handle python2/3 difference in raising exception        
    if PY2:
        exec('raise type, value, traceback', globals(), locals())
    else:
        raise value.with_traceback(traceback)


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
            event._returnval.put([result, exception])
        return True


caller = Caller()


def inmain(fn, *args, **kwargs):
    """Execute a function in the main thread. Wait for it to complete
    and return its return value.
    
    This function queues up a custom :code:`QEvent` to the Qt event loop.
    This event executes the specified function :code:`fn` in the Python 
    MainThread with the specified arguments and keyword arguments, and returns the result to the calling thread.
    
    This function can be used from the MainThread, but such use will just directly call the function, bypassing the Qt event loop.
    
    Arguments:
        fn: A reference to the function or method to run in the MainThread.
        
        *args: Any arguments to pass to :code:`fn` when it is called from the 
               MainThread.
        
        **kwargs: Any keyword arguments to pass to :code:`fn` when it is called
                  from the MainThread
                  
    Returns:
        The result of executing :code:`fn(*args, **kwargs)`
    """
    if threading.current_thread().name == 'MainThread':
        return fn(*args, **kwargs)
    return get_inmain_result(_in_main_later(fn, False, *args, **kwargs))


def inmain_later(fn, *args, **kwargs):
    """Queue up the executing of a function in the main thread and return immediately.
    
    This function queues up a custom :code:`QEvent` to the Qt event loop.
    This event executes the specified function :code:`fn` in the Python 
    MainThread with the specified arguments and keyword arguments, and returns 
    a Python Queue which will eventually hold the result from the executing of 
    :code:`fn`. To access the result, use :func:`qtutils.invoke_in_main.get_inmain_result`.
    
    This function can be used from the MainThread, but such use will just directly call the function, bypassing the Qt event loop.
    
    Arguments:
        fn: A reference to the function or method to run in the MainThread.
        
        *args: Any arguments to pass to :code:`fn` when it is called from the 
               MainThread.
        
        **kwargs: Any keyword arguments to pass to :code:`fn` when it is called
                  from the MainThread
                  
    Returns:
       A Python Queue which will eventually hold the result 
       :code:`(fn(*args, **kwargs), exception)` where 
       :code:`exception=[type,value,traceback]`.
    """
    return _in_main_later(fn, True, *args, **kwargs)


def _in_main_later(fn, exceptions_in_main, *args, **kwargs):
    """Asks the mainloop to call a function when it has time. Immediately
    returns the queue that was sent to the mainloop.  A call to queue.get()
    will return a list of [result,exception] where exception=[type,value,traceback]
    of the exception.  Functions are guaranteed to be called in the order
    they were requested."""
    queue = Queue()
    QCoreApplication.postEvent(caller, CallEvent(queue, exceptions_in_main, fn, *args, **kwargs))
    return queue


def get_inmain_result(queue):
    """ Processes the result of :func:`qtutils.invoke_in_main.inmain_later`.
    
    This function takes the queue returned by :code:`inmain_later` and blocks
    until a result is obtained. If an exception occurred when executing the
    function in the MainThread, it is raised again here (it is also raised in the
    MainThread). If no exception was raised, the result from the execution of the
    function is returned.
    
    Arguments:
        queue: The Python Queue object returned by :code:`inmain_later`
        
    Returns:
        The result from executing the function specified in the call to 
        :code:`inmain_later`
    
    """
    result, exception = queue.get()
    if exception is not None:
        _reraise(exception)
    return result


def inthread(f, *args, **kwargs):
    """A convenience function for starting a Python thread.
    
    This function launches a Python thread in Daemon mode, and returns a 
    reference to the running thread object.
    
    Arguments:
        f: A reference to the target function to be executed in the Python thread.
        
        *args: Any arguments to pass to :code:`f` when it is executed in the 
               new thread.
        
        **kwargs: Any keyword arguments to pass to :code:`f` when it is executed
                  in the new thread.
                  
    Returns:
        A reference to the (already running) Python thread object
    """
    thread = threading.Thread(target=f, args=args, kwargs=kwargs)
    thread.daemon = True
    thread.start()
    return thread


def inmain_decorator(wait_for_return=True, exceptions_in_main=True):
    """ A decorator which enforces the execution of the decorated thread to occur in the MainThread.
    
    This decorator wraps the decorated function or method in either 
    :func:`qtutils.invoke_in_main.inmain` or
    :func:`qtutils.invoke_in_main.inmain_later`.
    
    Keyword Arguments:
        wait_for_return: Specifies whether to use :code:`inmain` (if 
                         :code:`True`) or :code:`inmain_later` (if
                         :code:`False`).
                         
        exceptions_in_main: Specifies whether the exceptions should be raised
                            in the main thread or not. This is ignored if
                            :code:`wait_for_return=True`. If this is 
                            :code:`False`, then exceptions may be silenced if
                            you do not explicitly use
                            :func:`qtutils.invoke_in_main.get_inmain_result`.
                            
    Returns:
        The decorator returns a function that has wrapped the decorated function
        in the appropriate call to :code:`inmain` or :code:`inmain_later` (if 
        you are unfamiliar with how decorators work, please see the Python
        documentation).
        
        When calling the decorated function, the result is either the result of 
        the function executed in the MainThread (if :code:`wait_for_return=True`)
        or a Python Queue to be used with 
        :func:`qtutils.invoke_in_main.get_inmain_result` at a later time.
        
    """
    def wrap(fn):
        """A decorator which sets any function to always run in the main thread."""
        @functools.wraps(fn)
        def f(*args, **kwargs):
            if wait_for_return:
                return inmain(fn, *args, **kwargs)
            return _in_main_later(fn, exceptions_in_main, *args, **kwargs)
        return f
    return wrap


if __name__ == '__main__':
    import signal

    def loop(index):
        if index < 3:
            inthread(loop, index + 1)
        while True:
            # print('MyThread-%d: %s'%(index,str(QThread.currentThread())))
            # print('MyThread-%d: %s'%(index,threading.current_thread().name))
            # another_function(index)
            inmain(myFunction, index)

    def another_function(index):
        print('in thread-%d, running in thread: %s' % (index, threading.currentThread().name))

    def myFunction(index):
        print('from thread-%d, running in thread: %s' % (index, threading.currentThread().name))
        pass

    def myFunction2():
        print('from MainThread, running in thread: %s' % (threading.currentThread().name))
        QTimer.singleShot(0, lambda: inmain(myFunction2))

    qapplication = QCoreApplication(sys.argv)

    def sigint_handler(*args):
        qapplication.quit()

    signal.signal(signal.SIGINT, sigint_handler)

    thread = inthread(loop, 1)
    timer = QTimer.singleShot(0, lambda: inmain(myFunction2))
    qapplication.exec_()
