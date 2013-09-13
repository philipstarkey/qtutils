from PySide.QtCore import QSettings
import ast

class QSettingsWrapper(object):
    """A class that wraps QSettings to provide automatic type conversion
    and reduce the need for boilerplace code"""
    def __init__(self, companyname, appname, fields):
        self._qsettings = QSettings(companyname, appname)
        self._fields = fields
        if not self._qsettings.contains(self._fields[0]):
            # set default values to None:
            for name in self._fields:
                self._qsettings.setValue(name, repr(None))
        
    def __getattr__(self, name):
        if name in self._fields:
            return self._get(name)
        raise AttributeError
            
    def __setattr__(self, name, value):
        if hasattr(self, '_fields') and name in self._fields:
            self._set(name, value)
        object.__setattr__(self, name, value)
        
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
        
    
