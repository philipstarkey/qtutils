import qtutils.qt
if qtutils.qt.QT_ENV == 'Pyside':
    import qtutils.icons._icons_pyside
elif qtutils.qt.QT_ENV == 'PyQt4':
    import qtutils.icons._icons_pyqt4
elif qtutils.qt.QT_ENV == 'PyQt5':
    import qtutils.icons._icons_pyqt5
