from setuptools import setup
from pathlib import Path
from subprocess import check_call
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop


def build_icons(target_dir):
    icons_pyqt5 = target_dir / '_icons_pyqt5.py'
    icons_pyside6 = target_dir / '_icons_pyside6.py'
    qrc_file = Path('icons', 'icons.qrc')
    check_call(['pyrcc5', '-o', str(icons_pyqt5), str(qrc_file)])
    check_call(['pyside6-rcc', '-o', str(icons_pyside6), str(qrc_file)])


class custom_build_py(build_py):
    def run(self):
        if not self.dry_run:
            target_dir = Path(self.build_lib) / 'qtutils' / 'icons'
            target_dir.mkdir(parents=True, exist_ok=True)
            build_icons(target_dir)
        super().run()


class custom_develop(develop):
    def run(self):
        if not self.dry_run:
            target_dir = Path('.') / 'qtutils' / 'icons'
            self.mkpath(str(target_dir))
            build_icons(target_dir)
        super().run()


setup(cmdclass={'build_py': custom_build_py, 'develop': custom_develop})
