from setuptools import setup
import os
from pathlib import Path
from subprocess import check_call
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop


def build_icons(target_dir):
    icons_pyqt5 = target_dir / '_icons_pyqt5.py'
    icons_pyside2 = target_dir / '_icons_pyside2.py'
    qrc_file = Path('icons', 'icons.qrc')
    check_call(['pyrcc5', '-o', str(icons_pyqt5), str(qrc_file)])
    check_call(['pyside2-rcc', '-o', str(icons_pyside2), str(qrc_file)])


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


setup(
    use_scm_version={
        "version_scheme": "release-branch-semver",
        "local_scheme": os.getenv("SCM_LOCAL_SCHEME", "node-and-date"),
    },
    cmdclass={
        'build_py': custom_build_py,
        'develop': custom_develop,
    },
)
