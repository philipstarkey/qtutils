import qtutils.qt
try:
    if qtutils.qt.QT_ENV == qtutils.qt.PYSIDE2:
        import qtutils.icons._icons_pyside2
    elif qtutils.qt.QT_ENV == qtutils.qt.PYQT5:
        import qtutils.icons._icons_pyqt5
except ImportError:
    msg = """Can't import icon resource files. This package must be built before icons
        can be used, please install it or create in editable install with `pip install
        -e .`"""
    raise EnvironmentError(' '.join(msg.split()))
