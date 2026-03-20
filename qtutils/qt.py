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
import enum

PYSIDE6 = 'PySide6'
PYQT5 = 'PyQt5'
PYQT6 = 'PyQt6'
QT_ENV = None

libs = [PYQT5, PYSIDE6, PYQT6]
for lib in libs:
    if lib in sys.modules:
        QT_ENV = lib
        break
else:
    for lib in libs:
        try:
            __import__(lib)
            QT_ENV = lib
            break
        except ImportError:
            pass

if QT_ENV is None:
    raise Exception("No Qt Enviroment was detected!")

if QT_ENV == PYQT5:
    from PyQt5 import QtGui, QtCore, QtWidgets
elif QT_ENV == PYQT6:
    from PyQt6 import QtGui, QtCore, QtWidgets
elif QT_ENV == PYSIDE6:
    from PySide6 import QtGui, QtCore, QtWidgets
else:
    raise NotImplementedError(QT_ENV)

sys.modules['qtutils.qt.QtGui'] = QtGui
sys.modules['qtutils.qt.QtWidgets'] = QtWidgets
sys.modules['qtutils.qt.QtCore'] = QtCore

# Make Signal available under both names 'Signal' and 'pyqtSignal':
if QT_ENV in [PYQT5, PYQT6]:
    QtCore.Signal = QtCore.pyqtSignal
elif QT_ENV == [PYSIDE6]:
    QtCore.pyqtSignal = QtCore.Signal
else:
    raise NotImplementedError(QT_ENV)

# Make some names that moved from QtWidgets in Qt5 to QtGui in Qt6 available in both
# modules:
if QT_ENV == PYQT5:
    QtGui.QAction = QtWidgets.QAction
    QtGui.QShortcut = QtWidgets.QShortcut
elif QT_ENV in [PYSIDE6, PYQT6]:
    QtWidgets.QAction = QtGui.QAction
    QtWidgets.QDesktopWidget = QtGui.QScreen
    QtWidgets.QShortcut = QtGui.QShortcut
else:
    raise NotImplementedError(QT_ENV)

if QT_ENV == PYQT6:
    # Add shims for short enum names as supported in PyQt5 and PySide6:
    for module in (QtCore, QtGui, QtWidgets):
        for cls in [c for c in module.__dict__.values() if isinstance(c, type)]:
            for a in [a for a in cls.__dict__.values() if isinstance(a, enum.EnumMeta)]:
                for member in a:
                    if not hasattr(cls, member.name):
                        setattr(cls, member.name, member)
