#####################################################################
#                                                                   #
# UiLoader.py                                                       #
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

class UiLoaderPromotionException(Exception):
    pass

class UiLoaderUnknownWidgetException(Exception):
    pass
    
if 'PySide' in sys.modules.copy():
    from PySide.QtUiTools import QUiLoader
     
    class UiLoader(QUiLoader):
        """
        Class UiLoader
        
        This class subclasses QtUiTools.QUiLoader to implement custom promotion of
        widgets at runtime. This functionality also allows you to promote a 
        QMainWindow to your own class (which you cannot do in QtDesigner).
        
        When widgets are created, custom promotions are checked first, then 
        promotions in Qt designer. If neither of these apply, standard Qt widgets 
        are created.
        
        """
        def __init__(self, parent=None):
            QUiLoader.__init__(self, parent)
            self._store = []
            if parent is not None:
                self._store.append(parent)
            self._custom_widgets = {}
            self._promotions = {}
            self.toplevel_instance = None

        def registerCustomWidget(self, class_):
            """
            Register a class with the UiLoader that has been used with Qt Designers
            "promote to" functionality.
            """
            self._custom_widgets[class_.__name__] = class_
            QUiLoader.registerCustomWidget(self,class_)
            
        def registerCustomPromotion(self, name, class_):
            """
            Register a widget (name) that you wish to promote to the specified 
            class. This takes precedence over widgets promoted in Qt Designer
            """
            if name in self._promotions:
                raise UiLoaderPromotionException("The widget '%s' has already had a promotion registered"%name)
            self._promotions[name] = class_
                
        def createWidget(self, class_name, parent = None, name = ""):
            if self.toplevel_instance is not None and parent is None:
                widget = self.toplevel_instance
            elif name in self._promotions:
                widget = self._promotions[name](parent)   
                if parent is None:
                    # widgets with no parents must be saved or else Python crashes
                    self._store.append(widget)
            elif class_name in self._custom_widgets:
                widget = self._custom_widgets[class_name](parent)
            else:
                if class_name in self.availableWidgets():
                    widget = QUiLoader.createWidget(self, class_name, parent, name)
                else:
                    raise UiLoaderUnknownWidgetException("Widget '%s' has unknown class '%s'" %(name, class_name))
                
            return widget
            
        def load(self, uifile, toplevel_instance=None):
            """
            Load the .ui file specified in ui_file
            If toplevel_instance is specified, it will be returned as the toplevel widget instead of letting the QUiLoader creating a new one
            """
            self.toplevel_instance = toplevel_instance
            return QUiLoader.load(self, uifile)
        
else:
    from types import ModuleType
    from PyQt4 import uic
    
    class UiLoader(object):
        def __init__(self):
            # dummy module
            self.module = sys.modules['qtutils.widgets'] = ModuleType('widgets')    
        
        def registerCustomWidget(self, class_):
            self.registerCustomPromotion(class_.__name__, class_)
        
        def registerCustomPromotion(self, name, class_):
            if hasattr(self.module,name):
                 raise UiLoaderPromotionException("The widget '%s' has already had a promotion registered"%name)
            setattr(self.module, name, class_)
         
        def load(self, *args, **kwargs):
            return uic.loadUi(*args, **kwargs)
        
if __name__ == "__main__":
    loader = UiLoader()
    loader.registerCustomWidget(MyWidgetClassSpecifiedInQtDesignerPromoteTo)
    loader.registerCustomPromotion("myWidgetNameInQtDesigner",ClassToPromoteTo)
    ui = loader.load('myUiFile.ui')