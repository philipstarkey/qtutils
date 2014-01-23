#####################################################################
#                                                                   #
# UiLoader.py                                                       #
#                                                                   #
# Copyright 2013, Christopher Billington, Philip Starkey            #
#                                                                   #
# This file is part of the qtutils project                          #
# (see https://bitbucket.org/philipstarkey/qtutils )                #
# and is licensed under the Simplified BSD License.                 #
# See the license.txt file in the root of the project               #
# for the full license.                                             #
#                                                                   #
#####################################################################

from PySide.QtUiTools import QUiLoader

class UiLoaderPromotionException(Exception):
    pass

class UiLoaderUnknownWidgetException(Exception):
    pass
    
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
        if name in self._promotions:
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
        
if __name__ == "__main__":
    loader = UiLoader()
    loader.registerCustomWidget(MyWidgetClassSpecifiedInQtDesignerPromoteTo)
    loader.registerCustomPromotion("myWidgetNameInQtDesigner",ClassToPromoteTo)
    ui = loader.load('myUiFile.ui')