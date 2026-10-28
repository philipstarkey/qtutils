import os
from pathlib import Path
from qtutils.qt import QT_ENV, PYQT5, QtCore, QtGui, QtWidgets

THIS_DIR = Path(__file__).absolute().parent
ICONS_RCC = THIS_DIR / '_icons.rcc'

if not ICONS_RCC.exists():
    msg = f"""Icon resource file {ICONS_RCC} not found. This package must be built
    before icons can be used, please install it or create in editable install with `pip
    install -e .`"""
    raise EnvironmentError(' '.join(msg.split()))

QtCore.QResource.registerResource(str(ICONS_RCC))

if QT_ENV == PYQT5:
    # Qt 5 draws the 2× image of an icon only with this attribute set:
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

# Size at which the icons are designed to be drawn, in logical pixels:
ICON_SIZE = 16


def _at_2x(path):
    """The file name of the 2× variant of the image at `path`: '@2x' before the
    extension, or at the end if the name has no extension."""
    slash = max(path.rfind('/'), path.rfind('\\'))
    dot = path.rfind('.')
    if dot < slash:
        dot = len(path)
    return path[:dot] + '@2x' + path[dot:]


def add_file(icon, path, size=QtCore.QSize(), mode=QtGui.QIcon.Normal, state=QtGui.QIcon.Off):
    """Add the image at `path` to `icon` for the given mode and state, with its 2×
    variant ('name@2x.png') if there is one, so that the icon is drawn from the 2× image
    on a high-DPI screen. Qt itself adds the 2× variant only when a high-DPI screen is
    attached when the image is added, so an application started without one draws the
    1× image, scaled up, on a screen attached later."""
    icon.addFile(path, size, mode, state)
    if os.environ.get('QT_HIGHDPI_DISABLE_2X_IMAGE_LOADING'):
        return
    app = QtGui.QGuiApplication.instance()
    if app is not None and app.devicePixelRatio() > 1:
        # Qt has added the 2× variant:
        return
    path_2x = _at_2x(path)
    if QtCore.QFile.exists(path_2x):
        icon.addFile(path_2x, size, mode, state)


def Icon(path):
    """A QIcon of the image at `path` and its 2× variant, such as
    Icon(':/qtutils/fugue/tick')."""
    icon = QtGui.QIcon()
    add_file(icon, path)
    return icon


def in_mode(icon, mode, state=QtGui.QIcon.Off):
    """A QIcon that is drawn in every mode as `icon` is drawn in `mode`, for example a
    greyed-out icon on an enabled widget. The icon is rendered at ICON_SIZE for screens
    with device pixel ratios 1 and 2."""
    result = QtGui.QIcon()
    for scale in (1, 2):
        image = QtGui.QImage(
            ICON_SIZE * scale, ICON_SIZE * scale, QtGui.QImage.Format_ARGB32_Premultiplied
        )
        image.setDevicePixelRatio(scale)
        image.fill(0)
        painter = QtGui.QPainter(image)
        icon.paint(
            painter, QtCore.QRect(0, 0, ICON_SIZE, ICON_SIZE), QtCore.Qt.AlignCenter, mode, state
        )
        painter.end()
        result.addPixmap(QtGui.QPixmap.fromImage(image))
    return result
