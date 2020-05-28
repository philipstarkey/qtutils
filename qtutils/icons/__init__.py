import qtutils.qt
if qtutils.qt.QT_ENV == qtutils.qt.PYSIDE2:
    import qtutils.icons._icons_pyside2
elif qtutils.qt.QT_ENV == qtutils.qt.PYQT5:
    import qtutils.icons._icons_pyqt5
