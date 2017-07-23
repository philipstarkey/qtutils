import qtutils.qt
if qtutils.qt.QT_ENV is 'Pyside':
    import qtutils.icons._icons_pyside
elif qtutils.qt.QT_ENV is 'PyQt4':
        import qtutils.icons._icons_pyqt4
elif qtutils.qt.QT_ENV is 'PyQt5':
    import qtutils.icons._icons_pyqt5
