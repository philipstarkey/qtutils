#####################################################################
#                                                                   #
# qt.py                                                             #
#                                                                   #
# Copyright 2017, Jan Werkmann                                      #
#                                                                   #
# This file is part of the qtutils project                          #
# (see https://github.com/philipstarkey/qtutils )                   #
# and is licensed under the 2-clause, or 3-clause, BSD License.     #
# See the license.txt file in the root of the project               #
# for the full license.                                             #
#                                                                   #
# The purpose of this wrapper is to provide a abstraction layer     #
# around the different versions of QtGui, QtCore and QtWidgets.     #
# The warpper is supposed to act like PyQt5, but might need         #
# addition in some cases.                                           #
#####################################################################

import sys
import os
import enum
import importlib

PYSIDE6 = 'PySide6'
PYQT5 = 'PyQt5'
PYQT6 = 'PyQt6'

PYQT_LIBS = [PYQT5, PYQT6]
PYSIDE_LIBS = [PYSIDE6]
QT5_LIBS = [PYQT5]
QT6_LIBS = [PYQT6, PYSIDE6]

QT_LIBS = [PYQT5, PYSIDE6, PYQT6]


def _choose_qt_lib():
    # Check environment variable first:
    lib = os.getenv('QT_ENV')
    if lib is not None:
        if lib not in QT_LIBS:
            msg = f"Enviroment variable QT_ENV={lib} must be one of {','.join(QT_LIBS)}"
            raise EnvironmentError(msg)
        return lib

    # Check if a Qt library has already been imported:
    for lib in QT_LIBS:
        if f"{lib}.QtCore" in sys.modules:
            return lib

    # Choose any that is importable, in order defined in QT_LIBS:
    for lib in QT_LIBS:
        try:
            importlib.import_module(f"{lib}.QtCore")
            return lib
        except ImportError:
            continue

    raise EnvironmentError(f"No Qt library (of {','.join(QT_LIBS)}) found")


QT_ENV = _choose_qt_lib()

QtCore = importlib.import_module(f"{QT_ENV}.QtCore")
QtGui = importlib.import_module(f"{QT_ENV}.QtGui")
QtWidgets = importlib.import_module(f"{QT_ENV}.QtWidgets")

sys.modules['qtutils.qt.QtCore'] = QtCore
sys.modules['qtutils.qt.QtGui'] = QtGui
sys.modules['qtutils.qt.QtWidgets'] = QtWidgets


# Make Signal available under both names 'Signal' and 'pyqtSignal':
if QT_ENV in PYQT_LIBS:
    QtCore.Signal = QtCore.pyqtSignal
elif QT_ENV in PYSIDE_LIBS:
    QtCore.pyqtSignal = QtCore.Signal
else:
    raise NotImplementedError(QT_ENV)

# Make some names that moved from QtWidgets in Qt5 to QtGui in Qt6 available in both
# modules:
if QT_ENV in QT5_LIBS:
    QtGui.QAction = QtWidgets.QAction
    QtGui.QShortcut = QtWidgets.QShortcut
elif QT_ENV in QT6_LIBS:
    QtWidgets.QAction = QtGui.QAction
    QtWidgets.QDesktopWidget = QtGui.QScreen
    QtWidgets.QShortcut = QtGui.QShortcut
else:
    raise NotImplementedError(QT_ENV)

def _add_enum_aliases():
    for module in (QtCore, QtGui, QtWidgets):
        for cls in [c for c in module.__dict__.values() if isinstance(c, type)]:
            for a in [a for a in cls.__dict__.values() if isinstance(a, enum.EnumMeta)]:
                for name, member in a.__members__.items():
                    if not hasattr(cls, name):
                        setattr(cls, name, member)

if QT_ENV == PYQT6:
    # Add shims for short enum names in PyQt6 as supported in PyQt5 and PySide6:
    _add_enum_aliases()
    

# Add aliases for exec() and exec_(). The former doesn't exist in older PyQt5 versions
# (which needed to retain Python 2 compatibility), and the latter was removed in PyQt6.
# Both are present in PySide6.
if not hasattr(QtCore.QCoreApplication, 'exec'):
    QtCore.QCoreApplication.exec = QtCore.QCoreApplication.exec_
    QtWidgets.QDialog.exec = QtWidgets.QDialog.exec_
elif not hasattr(QtCore.QCoreApplication, 'exec_'):
    QtCore.QCoreApplication.exec_ = QtCore.QCoreApplication.exec
    QtWidgets.QDialog.exec_ = QtWidgets.QDialog.exec
