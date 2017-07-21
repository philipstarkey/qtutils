import sys
if 'Pyside' in sys.modules:
    import qtutils.icons._icons_pyside
else:
    try:
        import qtutils.icons._icons_pyqt4
    except:
        import qtutils.icons._icons_pyqt5
