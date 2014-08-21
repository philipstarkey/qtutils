import sys
if 'Pyside' in sys.modules:
    import qtutils.icons._icons_pyside
else:
    import qtutils.icons._icons_pyqt4
