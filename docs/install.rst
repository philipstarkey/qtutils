************
Installation
************
These installation instructions assume you already have Python installed. If you do not already have a copy of Python, we recommend you install `Anaconda Python`_. 

.. _`Anaconda Python`: https://www.continuum.io/downloads

----
PyPi
----
We recommend installing qtutils from the Python Package Index. To do this, open a terminal (linux/OSX) or command prompt (Windows) window, and run::

    pip install qtutils
    
-----------------
Upgrading qtutils
-----------------

To upgrade to the latest version of qtutils, run::

    pip install -U qtutils
    
To upgrade to a specific version of qtutils (or, alternatively, if you wish to downgrade), run::

    pip install -U qtutils==<version>
    
where :code:`<version>` is replaced by the version you wish (for example :code:`pip install -U qtutils==2.0.0`).

-------------------
Development Version
-------------------

If you wish to use the latest development version, you can obtain the source code from our `GitHub repository`_. Once you have cloned our repository, you should run :code:`python setup.py install` in order to build and install the qtutils package.


.. _`GitHub repository`: https://github.com/philipstarkey/qtutils
