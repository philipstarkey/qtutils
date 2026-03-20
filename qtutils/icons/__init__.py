from pathlib import Path
from qtutils.qt import QtCore

THIS_DIR = Path(__file__).absolute().parent
ICONS_RCC = THIS_DIR / '_icons.rcc'

if not ICONS_RCC.exists():
    msg = f"""Icon resource file {ICONS_RCC} not found. This package must be built
    before icons can be used, please install it or create in editable install with `pip
    install -e .`"""
    raise EnvironmentError(' '.join(msg.split()))

QtCore.QResource.registerResource(str(ICONS_RCC))

