#####################################################################
#                                                                   #
# qsettings_wrapper.py                                              #
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
if 'PySide' in sys.modules.copy():
    from PySide.QtCore import QSettings
else:
    from PyQt4.QtCore import QSettings
import ast

class type_with_properties(type):
    """A metaclass to create properties for a class based on the contents
    of its a class _fields. _fields should be a list of strings. At
    class creation, property getters and setters will be created,
    hooking each name up to _get and _set class methods."""
    def __init__(cls, name, superclasses, attrs):
        type.__init__(cls, name, superclasses, attrs)
        for name in cls._fields:
            method = property(lambda self, name=name: cls._get(self, name),
                              lambda self, value, name=name: cls._set(self, name, value))
            setattr(cls, name, method)
    
class QSettingsWrapper(object):
    """A class that wraps QSettings to provide automatic type conversion
    and reduce the need for boilerplace code"""
    __metaclass__ = type_with_properties
    _fields = [] # to be overridden by subclasses
    def __init__(self, companyname, appname):
        self._qsettings = QSettings(companyname, appname)
        # set default values to None:
        for name in self._fields:
            if not self._qsettings.contains(name):
                self._set(name, None)
        
    def _get(self, name):
        valrepr = self._qsettings.value(name)
        return ast.literal_eval(valrepr)
        
    def _set(self, name, value):
        valrepr = repr(value)
        try:
            assert value == ast.literal_eval(valrepr)
        except (ValueError, AssertionError, SyntaxError):
            raise ValueError('Value too complex to store. Can only store values for which x == ast.literal_eval(repr(x))')
        self._qsettings.setValue(name, valrepr)
        self._qsettings.sync()
        
        
if __name__ == '__main__':
    
    # Test and example implementation
    
    class TestSettings(QSettingsWrapper):
        _fields = ['test']
        def __init__(self):
            QSettingsWrapper.__init__(self, 'test', 'test')
            
    s = TestSettings()
    s.test = 5
    assert s.test == 5
    s.test += 2
    assert s.test == 7
    
