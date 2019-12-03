from __future__ import absolute_import, print_function

import sys
import os
import shutil
import py_compile
from setuptools import setup, Command
from runpy import run_path

try:
    from setuptools_conda import dist_conda
except ImportError:
    dist_conda = None


class build_icons(Command):
    # Do the build process for icon resource files. The idea is that someone like me
    # will run this before running sdist, so that the icon resources are included and
    # users do not need  pyrcc5/pyrcc5/pyside-rcc/pyside2-rcc on their systems in order
    # to install the package with icon support from pip or conda. Those installing from
    # a git clone however will have to have these tools and build the icon support they
    # want by running `python setup.py build._icons`.
    description = "Generate Qt icon resource files"
    user_options = [
        ('no-pyqt5', None, "Skip building the icon resource file for PyQt5"),
        ('no-pyqt4', None, "Skip building the icon resource file for PyQt4"),
        ('no-pyside', None, "Skip building the icon resource file for PySide"),
        ('no-pyside2', None, "Skip building the icon resource file for PySide2"),
        ('rebuild', None, "Rebuild the icons resources even if they already exist"),
    ]

    def initialize_options(self):
        self.no_pyqt5 = False
        self.no_pyqt4 = False
        self.no_pyside = False
        self.no_pyside2 = False
        self.rebuild = False

    def finalize_options(self):
        pass

    def run(self):
        print('building qt icon resource files ...')
        sys.path.insert(0, 'qtutils/icons')
        try:
            import _build

            _build.qrc(self.rebuild)
            if not self.no_pyqt5:
                _build.pyqt5(self.rebuild)
            if not self.no_pyqt4:
                _build.pyqt4(self.rebuild)
            if not self.no_pyside:
                _build.pyside(self.rebuild)
            if not self.no_pyside2:
                _build.pyside2(self.rebuild)
            print('done')
        finally:
            del sys.path[0]


package_data = {}
if 'CONDA_BUILD' in os.environ:
    # Make the conda packages a bit slimmer.

    # Don't include the raw icons or qrc file
    shutil.rmtree(os.path.join('qtutils', 'icons', 'fugue'))
    shutil.rmtree(os.path.join('qtutils', 'icons', 'custom'))
    os.unlink(os.path.join('qtutils', 'icons', 'icons.qrc'))
    os.unlink(os.path.join('qtutils', 'icons', '_build.py'))

    PY2 = sys.version_info.major == 2
    if PY2:
        # Pyside2 not supported on Python 2 so don't include it
        os.unlink(os.path.join('qtutils', 'icons', '_icons_pyside2.py'))
    else:
        # PySide not supported on Python 3 so don't include it
        os.unlink(os.path.join('qtutils', 'icons', '_icons_pyside.py'))


    # Include only compiled bytecode instead of source for the icon resources:
    package_data['qtutils.icons'] = []
    for file in [
        '_icons_pyqt5.py',
        '_icons_pyqt4.py',
        '_icons_pyside.py',
        '_icons_pyside2.py',
    ]:
        file = os.path.join('qtutils', 'icons', file)
        pycfile = file + 'c'
        if os.path.exists(file):
            kwargs = {} if PY2 else {'optimize': 2}
            py_compile.compile(file, pycfile, dfile=os.path.relpath(file), ** kwargs)
            os.unlink(file)
            package_data['qtutils.icons'].append(os.path.basename(pycfile))

    # Add an explanatory note for why the source is not here:
    with open(os.path.join('qtutils', 'icons', 'why_no_source.txt'), 'w') as f:
        f.write(
            ' '.join(
                """The Python source files containing Qt icon resources, and the PNG
                icons themselves, are exluded from conda packages in order to decrease
                package size. If you want to develop using Qt Designer and these icons,
                clone qtutils from github and use that instead.""".split()
            )
        )
    package_data['qtutils.icons'].append('why_no_source.txt')


# Empty right now. We don't depend on any particular Qt binding, since the user may use
# whichever they like
INSTALL_REQUIRES = []


cmdclass = {'build_icons': build_icons}
if dist_conda is not None:
    cmdclass['dist_conda'] = dist_conda

setup(
    name='qtutils',
    version=run_path(os.path.join('qtutils', '__version__.py'))['__version__'],
    description='Utilities for providing concurrent access to Qt objects, simplified QSettings storage, and dynamic widget promotion when loading UI files, in Python Qt applications. Also includes the Fugue icon set, by Yusuke Kamiyamane',
    long_description=open('README.md').read(),
    author='Philip Starkey',
    author_email='threepineapples@gmail.com',
    url='https://github.com/philipstarkey/qtutils',
    license="BSD, CC Attribution, UBUNTU FONT LICENCE",
    packages=['qtutils', 'qtutils.icons'],
    package_data=package_data,
    zip_safe=False,
    setup_requires=['setuptools', 'setuptools_scm'],
    include_package_data=True,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*",
    install_requires=INSTALL_REQUIRES if 'CONDA_BUILD' not in os.environ else [],
    cmdclass=cmdclass,
    command_options={
        'dist_conda': {
            'pythons': (__file__, ['3.6', '3.7', '3.8']),
            'platforms': (__file__, ['linux-64', 'win-32', 'win-64', 'osx-64']),
        },
    },
)
