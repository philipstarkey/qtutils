from setuptools import setup
import os
from pathlib import Path
from subprocess import check_call
import setuptools.command.build_py


class build_py(setuptools.command.build_py.build_py):
    def run(self):
        if not self.dry_run:
            target_dir = Path(self.build_lib) / 'qtutils' / 'icons'
            self.mkpath(str(target_dir))
            icons_pyqt5 = target_dir / '_icons_pyqt5.py'
            icons_pyside2 = target_dir / '_icons_pyside2.py'
            qrc_file = Path('icons', 'icons.qrc')
            check_call(['pyrcc5', '-o', str(icons_pyqt5), str(qrc_file)])
            check_call(['pyside2-rcc', '-o', str(icons_pyside2), str(qrc_file)])
        super().run()

setup(
    use_scm_version={
        "version_scheme": os.getenv("SCM_VERSION_SCHEME", "guess-next-dev"),
        "local_scheme": os.getenv("SCM_LOCAL_SCHEME", "node-and-date"),
    },
    cmdclass={'build_py': build_py},
)
