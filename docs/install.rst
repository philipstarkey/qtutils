************
Installation
************
These installation instructions assume you already have Python installed. If you do not already have a copy of Python, we recommend you install `Anaconda Python`_. 

.. _`Anaconda Python`: https://www.continuum.io/downloads

====
PyPi
====
To install qtutils from the Python Package Index run::

    pip install qtutils


Upgrading qtutils with PyPI
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To upgrade to the latest version of qtutils, run::

    pip install -U qtutils
    
To upgrade to a specific version of qtutils (or, alternatively, if you wish to downgrade), run::

    pip install -U qtutils==<version>
    
where :code:`<version>` is replaced by the version you wish (for example :code:`pip install -U qtutils==2.3.2`).
    
========
Anaconda
========
To install qtutils using `conda` run::

    conda install -c labscript-suite qtutils

.. note::
    The qtutils library is published on the labscript-suite anaconda cloud channel as it was created by labscript-suite developers for use in that software suite.

Upgrading qtutils with conda
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To upgrade to the latest version of qtutils, run::

    conda update -c labscript-suite qtutils
    
To upgrade to a specific version of qtutils (or, alternatively, if you wish to downgrade), run::

    conda update -c labscript-suite qtutils=<version>
    
where :code:`<version>` is replaced by the version you wish (for example :code:`conda update -c labscript-suite qtutils=3.0.0`).

===================
Development Version
===================

To install latest development version, clone the `GitHub repository`_ and run :code:`pip install .` to install, or :code:`pip install -e .` to install in 'editable' mode.

.. _`GitHub repository`: https://github.com/philipstarkey/qtutils
