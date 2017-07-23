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
import sys
import sip

PYSIDE = 'PySide'
PYQT4 = 'PyQt4'
PYQT5 = 'PyQt5'
QT_ENV = None


def set_pyqt4_API2():
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
    """If PyQt4 was already imported before we got a chance to set API version 2, ensure the API
    versions were already set to version 2. Otherwise confusing errors may occur later - better to catch this now"""
    API_NAMES = ["QDate", "QDateTime", "QString", "QTextStream", "QTime", "QUrl", "QVariant"]
    API_VERSION = 2
    for name in API_NAMES:
        try:
            if sip.getapi(name) != API_VERSION:
                raise RuntimeError("qtutils only compatible with version 2 of the  PYQt4 API. Either set the API to version 2 before importing PyQt4, or import qtutils first, which will set it for you")
        except ValueError:
            pass


libs = [PYQT5, PYQT4, PYSIDE]
for lib in libs:
    if lib in sys.modules:
        QT_ENV = lib
        if lib == PYQT4:
            check_pyqt4_api()
        break
else:
    for lib in libs:
        if lib == PYQT4:
            # Have to set pyqt API v2 before importing PyQt4:
            set_pyqt4_API2()
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
    QtCore.qInstallMessageHandler = QtCore.qInstallMsgHandler

sys.modules['qtutils.qt.QtGui'] = QtGui
sys.modules['qtutils.qt.QtWidgets'] = QtWidgets
sys.modules['qtutils.qt.QtCore'] = QtCore
