*************************************************************
Convenience functions for using Qt safely from Python threads
*************************************************************

QtUtils provides convenience functions for accessing Qt objects in a thread safe way. 
Qt requires that all GUI objects exist in the MainThread and that access to these objects is only made from the MainThread (see `Qt documentation`_).
This, while understandable, imposes significant limits on Python applications where threading is easy.
While there are solutions using Qt signals, slots and a :code:`QThread`, these require significant boiler plate code that we believe is unnecessary.

.. note:: There is some `debate`_ as to whether using Python threads with any part of the Qt library is safe, however this has been recently `challenged`_. The QtUtils library only instantiates a :code:`QEvent` and calls :code:`QCoreApplication.postEvent()` from a Python thread. It seems likely that as long as the underlying Python threading implementation matches the underlying Qt threading implementation **for your particular platform**, that there is no issue with how we have written this library. While we have not observed any issues with our library (and we have used it extensively on Windows, OSX and Ubuntu), this does not mean all platforms will behave in the same way. If this matters to you, we suggest you confirm the underlying thread implementation for your build of Python and Qt.

.. _`Qt documentation`: http://doc.qt.io/qt-5/threads-qobject.html
.. _`debate`: https://stackoverflow.com/q/1595649
.. _`challenged`: https://stackoverflow.com/a/49802578
  

========
Examples
========
We utilise the Qt event loop to execute arbitrary methods in the MainThread by posting a Qt event to the MainThread from a secondary thread.
QtUtils provides a function called :code:`inmain` which takes a reference to a method to execute in the MainThread, followed by any arguments to be passed to the method.

.. code-block:: python

    from qtutils import inmain

    # This is equivalent to calling my_func(arg1, arg2, foo=7, bar='baz') in the MainThread
    # The calling thread will wait for the result to be returned before continuing
    result = inmain(my_func, arg1, arg2, foo=7, bar='baz')
    
A call to :code:`inmain` blocks the calling thread until the Qt event loop can process our message, execute the specified method and return the result.
For situations where you don't wait to wait for the result, or you wish to do some other processing while waiting for the result, QtUtils provides the :code:`inmain_later` function.
This works in the same way as :code:`inmain`, but returns a reference to a Python :code:`Queue` object immediately.
The result can be retrieved from this queue at any time, as shown in the following example:
    
.. code-block:: python

    from qtutils import inmain_later, get_inmain_result

    # This is equivalent to calling my_func(arg1, arg2, foo=7, bar='baz') in the MainThread
    # The calling thread will immediately continue execution, and the result of the function
    # will be placed in the queue once the Qt event loop has processed the request
    queue = inmain_later(my_func, arg1, arg2, foo=7, bar='baz')
    # You can get the result (or raise any caught exceptions) by calling
    # Note that any exception will have already been raised in the MainThread
    result = get_inmain_result(queue)
    
This of course works directly with Qt methods as well as user defined functions/methods.
For example:

.. code-block:: python

    from qtutils import inmain_later, get_inmain_result, inthread

    def run_in_thread(a_line_edit, ignore=True):
        # set the text of the line edit, and wait for it to be set before continuing
        inmain(a_line_edit.setText, 'foobar')

        # Get the text of the line edit, and wait for it to be returned
        current_text = inmain(a_line_edit.text)

        # queue up a call to deselect() and don't wait for a result to be returned
        inmain_later(a_line_edit.deselect)

        # request the text of the line edit, but don't wait for it to be returned
        # However, this call is guaranteed to run AFTER the above inmain_later call
        queue = inmain_later(a_line_edit.text)

        # do some intensive calculations here

        # now get the text
        current_text = get_inmain_result(queue)
        print(current_text)

    # instantiate a QLineEdit
    # This object should only be accessed from the MainThread
    my_line_edit = QLineEdit()

    # starts a Python thread (in daemon mode) 
    # with target run_in_thread(my_line_edit, ignore=False)
    thread = inthread(run_in_thread,my_line_edit,ignore=False)
    
As you can see, the change between a direct call to a Qt method, and doing it in a thread safe way, is very simple:

.. code-block:: python

           a_line_edit.setText('foobar')
    inmain(a_line_edit.setText,'foobar')
    
We also provide decorators so that you can ensure the decorated method always runs in the MainThread regardless of the calling thread.
This is particularly useful when combined with Python properties.

.. code-block:: python

    # This function will always run in the MainThread, regardless of which thread calls it.
    # The calling thread will block until the function is run in the MainThread, and the result returned.
    # If called from the MainThread, the function is executed immediately as if you had called a_function()
    @inmain_decorator(wait_for_return=True)
    def a_function(a_line_edit):
        a_line_edit.setText('bar')
        return a_line_edit.text()

    # This function will always run in the MainThread, regardless of which thread calls it.
    # A call to this function will return immediately, and the function will be run at a
    # later time. A call to this function returns a python Queue.Queue() in which the result of
    # the decorated function will eventually be placed (or any exception raised)
    @inmain_decorator(wait_for_return=False)
    def another_function(a_line_edit):
        a_line_edit.setText('baz')
      

QtUtils also provides a convenience function for launching a Python thread in daemon mode.
:code:`inthread(target_method, arg1, arg2, ... kwarg1=False, kwargs2=7, ...)`

------------------
Exception handling
------------------
Typically, exceptions are raised in the calling thread. 
However, :code:`inmain_later` and the associated decorator will also raise the exception in the MainThread as there is no guarantee that the results will ever be read from the calling thread.
    
---------------------------------
Using QtUtils from the MainThread
---------------------------------
When using :code:`inmain`, or the associated decorator, QtUtils will bypass the Qt Event loop as just immediately execute the specified method. 
This avoids the obvious deadlock where the calling code is being executed by the Qt event loop, and is now waiting for the Qt event loop to execute the next event (which won't ever happen because it is blocked waiting for the next event by the calling code).
:code:`inmain_later` still posts an event to the Qt event loop when used from the MainThread.
This is useful if you want to execute something asynchronously from the MainThread (for example, asynchronously update the text of a label) but we recommend you do not attempt to read the result of such a call as you risk creating a deadlock.
    
--------------------------------------------------
What if I want to wait for user input in a thread?
--------------------------------------------------
If you want your thread to wait for user input, then this is not the library for you!
We suggest you check out how to `Wait in thread for user input from GUI`_ for a Qt solution and/or Python threading events for a Python solution.

.. _`Wait in thread for user input from GUI`: https://stackoverflow.com/a/35534047
    
=============
API reference
=============
.. automodule:: qtutils.invoke_in_main
    :members: