from __future__ import division, unicode_literals, print_function, absolute_import
import qtutils.qt
if qtutils.qt.QT_ENV == qtutils.qt.PYSIDE:
    import qtutils.icons._icons_pyside
elif qtutils.qt.QT_ENV == qtutils.qt.PYQT4:
    import qtutils.icons._icons_pyqt4
elif qtutils.qt.QT_ENV == qtutils.qt.PYQT5:
    import qtutils.icons._icons_pyqt5
