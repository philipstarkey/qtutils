# qtutils

[![Actions Status](https://github.com/philipstarkey/qtutils/workflows/Build%20and%20Release/badge.svg)](https://github.com/philipstarkey/qtutils/actions)
![GitHub release](https://img.shields.io/github/last-commit/philipstarkey/qtutils.svg)
[![Python Version](https://img.shields.io/pypi/pyversions/qtutils.svg)](https://python.org)
[![Documentation Status](https://readthedocs.org/projects/qtutils/badge/?version=stable)](https://qtutils.readthedocs.io/en/stable/?badge=stable)
[![PyPi Version](https://img.shields.io/pypi/v/qtutils.svg)](https://pypi.python.org/pypi/qtutils/) 
[![Conda Version](https://img.shields.io/conda/v/labscript-suite/qtutils)](https://anaconda.org/labscript-suite/qtutils)
[![PyPi License](https://img.shields.io/pypi/l/qtutils.svg)](https://github.com/philipstarkey/qtutils/blob/master/LICENSE.txt) 

Utilities for providing concurrent access to Qt objects, simplified QSettings storage,
and dynamic widget promotion when loading UI files, in Python Qt applications. Includes
the Fugue icon set, free to use with attribution to Yusuke Kamiyamane.

* [Documentation](https://qtutils.readthedocs.io)
* [PyPI](https://pypi.python.org/pypi/qtutils/)
* [Source code (GitHub)](https://github.com/philipstarkey/qtutils)


## Installation

* To install the latest release version, run `pip install qtutils`.

* To install latest development version, clone the GitHub repository and run `pip
  install .` to install, or `pip install -e .` to install in 'editable' mode.
   
   
## Summary

`qtutils` is a Python library that provides some convenient features to Python
applications using the PyQt5/PySide2 widget library.

`qtutils` 3.0 dropped support for Python 2.7, PyQt4 and PySide. If you need to use these
platforms, you may use `qtutils` 2.3.2 or earlier.

`qtutils` contains the following components:

* `invoke_in_main`: This provides some helper functions to interact with Qt from
  threads.

* `UiLoader`: This provides a simplified means of promoting widgets in `*.ui` files to a
  custom widget of your choice.

* `qsettings_wrapper`: A wrapper around QSettings which allows you to access keys of
  QSettings as instance attributes. It also performs automatic type conversions.

* `icons`: An icon set as a `QResource` file and corresponding Python module. The
  resulting resource file can be used by Qt designer, and the python module imported by
  applications to make the icons available to them. The Fugue icon set was made by
  Yusuke Kamiyamane, and is licensed under a Creative Commons Attribution 3.0 License.
  If you can't or don't want to provide attribution, please purchase a royalty-free
  license from http://p.yusukekamiyamane.com/

* `Qt`: a PyQt5/PySide2 agnostic interface to Qt that allows you to write software using
  the PyQt5 API but have it run on either PyQt5 or PySide2.

* `outputbox`: a `QTextEdit` widget for displaying log/output text of an application,
  either by calling methods or by sending data to it over `zeromq`.


## Using icons with Qt designer

To use the icons from Qt designer, clone this repository, and point Qt designer to the
`.qrc` file for the icons set: `icons/icons.qrc`. Unfortunately Qt desginer saves the
absolute path to this file in the resulting `.ui` file, so if the `.ui` file is later
edited by someone on another system, they will see an error at startup saying the `.qrc`
file cannot be found. This can be ignored and the `.ui` file will still function
correctly, but Qt designer will need to be told the local path to the `.qrc` file before
it can display the icons within its interface.
