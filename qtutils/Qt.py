#####################################################################
#                                                                   #
# Qt.py                                                             #
#                                                                   #
# Copyright 2017, Jan Werkmann                                      #
#                                                                   #
# This file is part of the qtutils project                          #
# (see https://bitbucket.org/philipstarkey/qtutils )                #
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

PYSIDE = 'PySide'
PYQT4 = 'PyQt4'
PYQT5 = 'PyQt5'

libs = [PYQT5, PYQT4, PYSIDE]
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
else:
    if QT_ENV == PYQT4:
        from PyQt4 import QtGui, QtCore

    elif QT_ENV == PYSIDE:
        from PySide import QtGui, QtCore
        import PySide
        QtCore.QT_VERSION_STR = PySide.QtCore.__version__
        QtCore.PYQT_VERSION_STR = PySide.__version__

    class NewQHeaderView(QtGui.QHeaderView):
        def setSectionsMovable(self, *args, **kwargs):
            self.setMovable(*args, **kwargs)

        def setSectionsClickable(self, *args, **kwargs):
            self.setClickable(*args, **kwargs)

        def setSectionResizeMode(self, *args, **kwargs):
            self.setResizeMode(*args, **kwargs)

    QtGui.QHeaderView = NewQHeaderView

    class NewQFileDialog(QtGui.QFileDialog):
        def getOpenFileName(self, *args, **kwargs):
            self.getOpenFileNamesAndFilter(*args, **kwargs)

    QtGui.QFileDialog = NewQFileDialog

    QtWidgets = QtGui
    QtCore.QSortFilterProxyModel = QtGui.QSortFilterProxyModel
    QtWidgets.QStyleOptionProgressBar = QtGui.QStyleOptionProgressBarV2

sys.modules['qtutils.Qt.QtGui'] = QtGui
sys.modules['qtutils.Qt.QtWidgets'] = QtWidgets
sys.modules['qtutils.Qt.QtCore'] = QtCore
