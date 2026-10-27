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

import os
import sys
import warnings
import xml.etree.ElementTree as ET

import qtutils.qt
from qtutils.qt import QtCore, QtGui, QtWidgets
from qtutils.iconlabel import IconLabel


class UiLoaderPromotionException(Exception):
    pass


class UiLoaderUnknownWidgetException(Exception):
    pass


# The role elements of an <iconset> in a .ui file, with the icon mode and state of each:
_ICONSET_ROLES = {
    'normaloff': (QtGui.QIcon.Normal, QtGui.QIcon.Off),
    'normalon': (QtGui.QIcon.Normal, QtGui.QIcon.On),
    'disabledoff': (QtGui.QIcon.Disabled, QtGui.QIcon.Off),
    'disabledon': (QtGui.QIcon.Disabled, QtGui.QIcon.On),
    'activeoff': (QtGui.QIcon.Active, QtGui.QIcon.Off),
    'activeon': (QtGui.QIcon.Active, QtGui.QIcon.On),
    'selectedoff': (QtGui.QIcon.Selected, QtGui.QIcon.Off),
    'selectedon': (QtGui.QIcon.Selected, QtGui.QIcon.On),
}


def _parse_ui(uifile):
    """The XML tree of a .ui file given as a path or a file object, and the directory
    that relative image paths in it are relative to."""
    if hasattr(uifile, 'read'):
        root = ET.parse(uifile).getroot()
        uifile.seek(0)
        return root, ''
    uifile = os.fspath(uifile)
    return ET.parse(uifile).getroot(), os.path.dirname(uifile)


def _iconset_icon(element, base_dir):
    """A QIcon from an <iconset> element, with the 2× variant of each image."""
    # Imported here so that qtutils can be imported without the built icon resource:
    from qtutils.icons import add_file

    theme = element.get('theme')
    if theme and QtGui.QIcon.hasThemeIcon(theme):
        return QtGui.QIcon.fromTheme(theme)
    roles = [(child.tag, child.text) for child in element if child.tag in _ICONSET_ROLES]
    if not roles:
        roles = [('normaloff', element.text)]
    icon = QtGui.QIcon()
    for role, path in roles:
        if not path:
            continue
        path = path.strip()
        if not path.startswith(':') and not os.path.isabs(path):
            path = os.path.join(base_dir, path)
        mode, state = _ICONSET_ROLES[role]
        add_file(icon, path, QtCore.QSize(), mode, state)
    return icon


def _find(toplevel, cls, name):
    if toplevel.objectName() == name and isinstance(toplevel, cls):
        return toplevel
    obj = toplevel.findChild(cls, name)
    if obj is None:
        raise UiLoaderUnknownWidgetException(f"No {cls.__name__} named {name!r}")
    return obj


def _set_icons(toplevel, root, base_dir, uifile):
    """Set every icon that the .ui file gives as an <iconset> on the loaded widgets
    again, with the 2× variant of each image added. Qt's form builder and PyQt's uic
    add the 2× variants only for some icons and only when a high-DPI screen is attached
    when the file is loaded."""
    parents = {child: parent for parent in root.iter() for child in parent}
    for element in root.iter('iconset'):
        prop = parents[element]
        owner = parents[prop]
        name = prop.get('name')
        icon = _iconset_icon(element, base_dir)
        if prop.tag == 'property' and owner.tag == 'widget':
            _find(toplevel, QtWidgets.QWidget, owner.get('name')).setProperty(name, icon)
        elif prop.tag == 'property' and owner.tag == 'action':
            _find(toplevel, QtGui.QAction, owner.get('name')).setProperty(name, icon)
        elif prop.tag == 'attribute' and owner.tag == 'widget' and name == 'icon':
            # The icon of a page of a QTabWidget or QToolBox:
            page = _find(toplevel, QtWidgets.QWidget, owner.get('name'))
            container = _find(toplevel, QtWidgets.QWidget, parents[owner].get('name'))
            if isinstance(container, QtWidgets.QTabWidget):
                container.setTabIcon(container.indexOf(page), icon)
            elif isinstance(container, QtWidgets.QToolBox):
                container.setItemIcon(container.indexOf(page), icon)
            else:
                warnings.warn(f"{uifile}: icon of page {owner.get('name')!r} of a "
                              f"{type(container).__name__} is not set with its 2× variant")
        elif prop.tag == 'property' and owner.tag == 'item' and name == 'icon':
            # An item of a QComboBox or QListWidget:
            container_element = parents[owner]
            container = _find(toplevel, QtWidgets.QWidget, container_element.get('name'))
            index = [e for e in container_element if e.tag == 'item'].index(owner)
            if isinstance(container, QtWidgets.QComboBox):
                container.setItemIcon(index, icon)
            elif isinstance(container, QtWidgets.QListWidget):
                container.item(index).setIcon(icon)
            else:
                warnings.warn(f"{uifile}: icon of item {index} of "
                              f"{container_element.get('name')!r} is not set with its 2× variant")
        else:
            warnings.warn(f"{uifile}: icon in <{prop.tag} name={name!r}> of <{owner.tag}> "
                          f"is not set with its 2× variant")


if qtutils.qt.QT_ENV in [qtutils.qt.PYSIDE6]:
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt

    # QUiLoader sets this attribute, but it must be set before instantiating a
    # QApplication to have any effect - otherwise only a warning is printed. On the
    # other hand, We can't actually load UI files until after instantiating a
    # QApplication. Therefore we set this now, before instantiating a QApplication.
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

    class UiLoader(QUiLoader):
        """
        Class UiLoader

        This class subclasses QtUiTools.QUiLoader to implement custom promotion of
        widgets at runtime. This functionality also allows you to promote a
        QMainWindow to your own class (which you cannot do in QtDesigner).

        When widgets are created, custom promotions are checked first, then
        promotions in Qt designer. If neither of these apply, standard Qt widgets
        are created.

        Every icon in the file gets the 2× variant of its image, and a widget promoted
        to IconLabel with the header qtutils/widgets.h is a qtutils.iconlabel.IconLabel.
        """

        def __init__(self, parent=None):
            QUiLoader.__init__(self, parent)
            self._promotions = {}
            self._store = []
            self.toplevel_instance = None
            self.registerCustomWidget(IconLabel)

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
            root, base_dir = _parse_ui(uifile)
            toplevel = super().load(uifile)
            _set_icons(toplevel, root, base_dir, uifile)
            return toplevel

elif qtutils.qt.QT_ENV in [qtutils.qt.PYQT5, qtutils.qt.PYQT6]:
    from types import ModuleType

    if qtutils.qt.QT_ENV == qtutils.qt.PYQT5:
        from PyQt5 import uic
    else:
        from PyQt6 import uic


    class UiLoader(object):
        """
        Loads .ui files with uic.loadUi, with the widgets promoted in Qt Designer
        with the header qtutils/widgets.h taken from the classes registered with
        registerCustomWidget() and registerCustomPromotion(). Every icon in the file
        gets the 2× variant of its image, and a widget promoted to IconLabel is a
        qtutils.iconlabel.IconLabel.
        """
        def __init__(self):
            # dummy module
            self.module = sys.modules['qtutils.widgets'] = ModuleType('widgets')
            self.registerCustomWidget(IconLabel)

        def registerCustomWidget(self, class_):
            self.registerCustomPromotion(class_.__name__, class_)

        def registerCustomPromotion(self, name, class_):
            if hasattr(self.module, name):
                raise UiLoaderPromotionException("The widget '%s' has already had a promotion registered" % name)
            setattr(self.module, name, class_)

        def load(self, uifile, *args, **kwargs):
            root, base_dir = _parse_ui(uifile)
            toplevel = uic.loadUi(uifile, *args, **kwargs)
            _set_icons(toplevel, root, base_dir, uifile)
            return toplevel

else:
    raise ValueError(qtutils.qt.QT_ENV)

if __name__ == "__main__":
    loader = UiLoader()
    loader.registerCustomWidget(MyWidgetClassSpecifiedInQtDesignerPromoteTo)
    loader.registerCustomPromotion("myWidgetNameInQtDesigner", ClassToPromoteTo)
    ui = loader.load('myUiFile.ui')
