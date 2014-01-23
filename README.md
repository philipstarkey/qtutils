# QtUtils

Utilities for providing concurrent access to Qt objects, simplified QSettings storage, and dynamic widget promotion when loading UI files, in Python Qt applications.
( 
[view on pypi](https://pypi.python.org/pypi/qtutils/);
[view on Bitbucket](https://bitbucket.org/philipstarkey/qtutils)
)

   * Install the latest development version by cloning the bitbucket repository and running `python setup.py install` 
   * Install the latest release version using `pip install qtutils` or `easy_install qtutils`
   
   

QtUtils is a Python library that provides some convenient features to Python applications using the PyQt/PySide widget library.

QtUtils contains the following components:

* [invoke_in_main](https://bitbucket.org/philipstarkey/qtutils/wiki/invoke_in_main): This provides some helper functions to interact with Qt from threads. 

* UiLoader: This provides a simplified means of promoting widgets in *.ui files to a custom widget of your choice.

* qsettings_wrapper: A wrapper around QSettings which allows you to access keys of QSettings as instance attributes. It also performs automatic type conversions.