from pathlib import Path
from subprocess import check_call

# This script builds PySide2 and PyQt5 icon resource .py files, and a .qrc file for use
# with e.g. Qt designer.

# This script requires the pyqt5 `pyrcc5` tool and the PySide2 `pyside2-rcc` tool. These
# are available with the PyQt5 and PySide2 PyPI packages.

here = Path(__file__).parent


icon_folders = [here / 'custom', here / 'fugue']
qrc_file = Path(here, 'icons.qrc')


HEADER = """<!DOCTYPE RCC><RCC version="1.0">
  <qresource  prefix="/qtutils">"""

FOOTER = """  </qresource>
</RCC>"""


def make_qrc_file():
    lines = [HEADER]
    for folder in icon_folders:
        for filename in folder.iterdir():
            lines.append(f"    <file>{folder.name}/{filename.name}</file>")
    lines.append(FOOTER)
    qrc_file.write_text("\n".join(lines))


def make_dot_py_files():
    target_dir = here.parent / 'qtutils' / 'icons'
    icons_pyqt5 = target_dir / '_icons_pyqt5.py'
    icons_pyside2 = target_dir / '_icons_pyside2.py'
    check_call(['pyrcc5', '-o', str(icons_pyqt5), str(qrc_file)])
    check_call(['pyside2-rcc', '-o', str(icons_pyside2), str(qrc_file)])


if __name__ == '__main__':
    make_qrc_file()
    make_dot_py_files()
