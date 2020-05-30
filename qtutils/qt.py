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

PYSIDE2 = 'PySide2'
PYQT5 = 'PyQt5'
QT_ENV = None

libs = [PYQT5, PYSIDE2]
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
elif QT_ENV == PYSIDE2:
    from PySide2 import QtGui, QtCore, QtWidgets

sys.modules['qtutils.qt.QtGui'] = QtGui
sys.modules['qtutils.qt.QtWidgets'] = QtWidgets
sys.modules['qtutils.qt.QtCore'] = QtCore

# Make Signal available under both names 'Signal' and 'pyqtSignal':
if QT_ENV ==  PYQT5:
    QtCore.Signal = QtCore.pyqtSignal
else:
    QtCore.pyqtSignal = QtCore.Signal
