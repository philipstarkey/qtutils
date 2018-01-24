#####################################################################
#                                                                   #
# qt.py                                                             #
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

from __future__ import division, unicode_literals, print_function, absolute_import

import sys

PYSIDE = 'PySide'
PYQT4 = 'PyQt4'
PYQT5 = 'PyQt5'
QT_ENV = None


def set_pyqt4_api():
    import sip
    # This must be done before importing PyQt4:
    API_NAMES = ["QDate", "QDateTime", "QString", "QTextStream", "QTime", "QUrl", "QVariant"]
    API_VERSION = 2
    for name in API_NAMES:
        try:
            sip.setapi(name, API_VERSION)
        except ValueError:
            pass


def check_pyqt4_api():
    """If PyQt4 was already imported before we got a chance to set API version
    2, ensure the API versions are either not set, or set to version 2.
    Otherwise confusing errors may occur later - better to catch this now"""
    import sip
    API_NAMES = ["QDate", "QDateTime", "QString", "QTextStream", "QTime", "QUrl", "QVariant"]
    API_VERSION = 2
    for name in API_NAMES:
        try:
            if sip.getapi(name) != API_VERSION:
                msg = ("qtutils is only compatible with version 2 of the  PyQt4 API." +
                       "Whilst you can import PyQt4 prior to importing qtutils (in order to tell qtutils " +
                       "to use PyQt4), either set the API version to 2 yourself, or import qtutils " +
                       "(which will set it for you) prior to importing QtGui or QtCore.")
                raise RuntimeError(msg)
        except ValueError:
            # API version not set yet.
            pass


libs = [PYQT5, PYQT4, PYSIDE]
for lib in libs:
    if lib in sys.modules:
        QT_ENV = lib
        if lib == PYQT4:
            check_pyqt4_api()
            set_pyqt4_api()
        break
else:
    for lib in libs:
        if lib == PYQT4:
            # Have to set pyqt API v2 before importing PyQt4:
            set_pyqt4_api()
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

    # Allow the methods that have been renamed in Qt5 to be accessed by their
    # Qt5 names:
    QtGui.QHeaderView.setSectionsMovable = QtGui.QHeaderView.__dict__["setMovable"]
    QtGui.QHeaderView.setSectionsClickable = QtGui.QHeaderView.__dict__["setClickable"]
    QtGui.QHeaderView.setSectionResizeMode = QtGui.QHeaderView.__dict__["setResizeMode"]

    if QT_ENV == PYQT4:
        # Pyside does not have the methods ending in "-AndFilter":
        QtGui.QFileDialog.getOpenFileName = QtGui.QFileDialog.__dict__["getOpenFileNameAndFilter"]
        QtGui.QFileDialog.getOpenFileNames = QtGui.QFileDialog.__dict__["getOpenFileNamesAndFilter"]
        QtGui.QFileDialog.getSaveFileName = QtGui.QFileDialog.__dict__["getSaveFileNameAndFilter"]

    QtWidgets = QtGui
    QtCore.QSortFilterProxyModel = QtGui.QSortFilterProxyModel
    QtCore.QItemSelectionModel = QtGui.QItemSelectionModel
    QtWidgets.QStyleOptionProgressBar = QtGui.QStyleOptionProgressBarV2
    QtWidgets.QStyleOptionTab = QtGui.QStyleOptionTabV3
    QtWidgets.QStyleOptionViewItem = QtGui.QStyleOptionViewItemV4
    QtCore.qInstallMessageHandler = QtCore.qInstallMsgHandler

sys.modules['qtutils.qt.QtGui'] = QtGui
sys.modules['qtutils.qt.QtWidgets'] = QtWidgets
sys.modules['qtutils.qt.QtCore'] = QtCore
