# QtUtils

[![PyPi Version](https://img.shields.io/pypi/v/qtutils.svg)](https://pypi.python.org/pypi/qtutils/) 
[![Documentation Status](https://readthedocs.org/projects/qtutils/badge/?version=stable)](https://qtutils.readthedocs.io/en/stable/?badge=stable)
![GitHub release](https://img.shields.io/github/last-commit/philipstarkey/qtutils.svg)
[![PyPi License](https://img.shields.io/pypi/l/qtutils.svg)](https://github.com/philipstarkey/qtutils/blob/master/LICENSE.txt) 

Utilities for providing concurrent access to Qt objects, simplified QSettings storage, and dynamic widget promotion when loading UI files, in Python Qt applications.
Includes the Fugue icon set, free to use with attribution to Yusuke Kamiyamane.

* [Documentation](https://qtutils.readthedocs.io)
* [PyPI](https://pypi.python.org/pypi/qtutils/)
* [Source code (GitHub)](https://github.com/philipstarkey/qtutils)


## Installation

   * Install the latest release version using `pip install qtutils` or `easy_install qtutils`
   * Install the latest development version by cloning the GitHub repository and running `python setup.py install` 
   
   
## Summary

QtUtils is a Python library that provides some convenient features to Python applications using the PyQt/PySide widget library.

QtUtils contains the following components:

* invoke_in_main: This provides some helper functions to interact with Qt from threads. 

* UiLoader: This provides a simplified means of promoting widgets in *.ui files to a custom widget of your choice.

* qsettings_wrapper: A wrapper around QSettings which allows you to access keys of QSettings as instance attributes. It also performs automatic type conversions.

* icons: An icon set that is automatically built into a QResource file and corresponding Python module on import. The resulting resource file can be used by Qt designer, and the python module imported by applications to make the icons available to them. The Fugue icon set was made by Yusuke Kamiyamane, and is licensed under a Creative Commons Attribution 3.0 License. If you can't or don't want to provide attribution, please purchase a royalty-free license from http://p.yusukekamiyamane.com/

* Qt: a PyQt/PySide agnostic interface to Qt that allows you to write software using the PyQt5 API but have it run on either PyQt5, PyQt4 or PySide v1.
