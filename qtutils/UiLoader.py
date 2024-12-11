#####################################################################
#                                                                   #
# UiLoader.py                                                       #
#                                                                   #
# Copyright 2013, Christopher Billington, Philip Starkey            #
#                                                                   #
# This file is part of the qtutils project                          #
# (see https://github.com/philipstarkey/qtutils )                   #
# and is licensed under the 2-clause, or 3-clause, BSD License.     #
# See the license.txt file in the root of the project               #
# for the full license.                                             #
#                                                                   #
#####################################################################

import sys

import qtutils.qt


class UiLoaderPromotionException(Exception):
    pass


class UiLoaderUnknownWidgetException(Exception):
    pass


if qtutils.qt.QT_ENV in [qtutils.qt.PYSIDE6]:
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt

    # QUiLoader sets this attribute, but it must be set before instantiating a
    # QApplication to have any effect - otherwise only a warning is printed. On the
    # other hand, We can't actually load UI files until after instantiating a
    # QApplication. Therefore we set this now, before instantiating a QApplication.
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

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
            self._promotions = {}
            self._store = []
            self.toplevel_instance = None

        def registerCustomPromotion(self, name, class_):
            """
            Register a widget (name) that you wish to promote to the specified
            class. This takes precedence over widgets promoted in Qt Designer
            """
            if name in self._promotions:
                raise UiLoaderPromotionException("The widget '%s' has already had a promotion registered" % name)
            self._promotions[name] = class_

        def createWidget(self, class_name, parent=None, name=""):
            if name in self._promotions:
                widget = self._promotions[name](parent)
                if parent is None:
                    self._store.append(widget) # hold a reference until loading complete
                return widget
            if parent is None and self.toplevel_instance is not None:
                return self.toplevel_instance
            return super().createWidget(class_name, parent, name)

        def load(self, uifile, toplevel_instance=None):
            """
            Load the .ui file specified in ui_file
            If toplevel_instance is specified, it will be returned as the toplevel widget instead of letting the QUiLoader creating a new one
            """
            self.toplevel_instance = toplevel_instance
            return super().load(uifile)

else:
    from types import ModuleType
    from PyQt5 import uic

    class UiLoader(object):
        def __init__(self):
            # dummy module
            self.module = sys.modules['qtutils.widgets'] = ModuleType('widgets')

        def registerCustomWidget(self, class_):
            self.registerCustomPromotion(class_.__name__, class_)

        def registerCustomPromotion(self, name, class_):
            if hasattr(self.module, name):
                raise UiLoaderPromotionException("The widget '%s' has already had a promotion registered" % name)
            setattr(self.module, name, class_)

        def load(self, *args, **kwargs):
            return uic.loadUi(*args, **kwargs)


if __name__ == "__main__":
    loader = UiLoader()
    loader.registerCustomWidget(MyWidgetClassSpecifiedInQtDesignerPromoteTo)
    loader.registerCustomPromotion("myWidgetNameInQtDesigner", ClassToPromoteTo)
    ui = loader.load('myUiFile.ui')
