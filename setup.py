from __future__ import absolute_import, print_function
from setuptools import setup
import sys
import os

try:
    from setuptools_conda import conda_dist
except ImportError:
    conda_dist = None


BUILD_PYQT5_ICONS_RESOURCE = True
BUILD_PYQT4_ICONS_RESOURCE = True
BUILD_PYSIDE_ICONS_RESOURCE = True
BUILD_PYSIDE2_ICONS_RESOURCE = True

if 'NO_PYSIDE' in sys.argv:
    sys.argv.remove('NO_PYSIDE')
    BUILD_PYSIDE_ICONS_RESOURCE = False
if 'NO_PYSIDE2' in sys.argv:
    sys.argv.remove('NO_PYSIDE2')
    BUILD_PYSIDE2_ICONS_RESOURCE = False
if 'NO_PYQT4' in sys.argv:
    BUILD_PYQT4_ICONS_RESOURCE = False
    sys.argv.remove('NO_PYQT4')
if 'NO_PYQT5' in sys.argv:
    BUILD_PYQT5_ICONS_RESOURCE = False
    sys.argv.remove('NO_PYQT5')

# Set to True to rebuild resource files even if they exist. This may be necessary if
# adding new icons.
REBUILD = False
if 'REBUILD' in sys.argv:
    sys.argv.remove('REBUILD')
    REBUILD = True

VERSION = '2.3.1'

# conditional for readthedocs environment
on_rtd = os.environ.get('READTHEDOCS') == 'True'
if not on_rtd:
    # Do the build process for icon resource files, this will only do anything
    # if the files are not already present.  The idea is that someone like me
    # will run this during sdist, upload the results to PyPI, and then the
    # files should already be there for those installing via easy_install
    # or pip. So those people will not require pyside-rcc or pyrcc4 on
    # their systems in order to install icon support for both PyQt4 and
    # Pyside. Those installing from an hg clone however will have to have
    # pyside-rcc and pyrcc4 installed for the following to work, or they
    # can disable one of the via the boolean flags at the top of this file.
    print('building qt icon resource files ...')
    sys.path.insert(0, 'qtutils/icons')
    import _build
    _build.qrc(REBUILD)
    if BUILD_PYQT5_ICONS_RESOURCE:
        _build.pyqt5(REBUILD)
    if BUILD_PYQT4_ICONS_RESOURCE:
        _build.pyqt4(REBUILD)
    if BUILD_PYSIDE_ICONS_RESOURCE:
        _build.pyside(REBUILD)
    if BUILD_PYSIDE2_ICONS_RESOURCE:
        _build.pyside2(REBUILD)
    print('done')
else:
    print('Skipping icon building on readthedocs...')

# Auto generate a __version__ package for the package to import
with open(os.path.join('qtutils', '__version__.py'), 'w') as f:
    f.write("__version__ = '%s'\n" % VERSION)

# Empty right now. We don't depend on any particular Qt binding, since the user may use
# whichever they like
INSTALL_REQUIRES = []

setup(
    name='qtutils',
    version=VERSION,
    description='Utilities for providing concurrent access to Qt objects, simplified QSettings storage, and dynamic widget promotion when loading UI files, in Python Qt applications. Also includes the Fugue icon set, by Yusuke Kamiyamane',
    long_description=open('README.md').read(),
    author='Philip Starkey',
    author_email='threepineapples@gmail.com',
    url='https://github.com/philipstarkey/qtutils',
    license="BSD, CC Attribution, UBUNTU FONT LICENCE",
    packages=['qtutils', 'qtutils.icons'],
    zip_safe=False,
    setup_requires=['setuptools', 'setuptools_scm'],
    include_package_data=True,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5",
    install_requires=INSTALL_REQUIRES if 'CONDA_BUILD' not in os.environ else [],
    cmdclass={'conda_dist': conda_dist} if conda_dist is not None else {},
    command_options={
        'conda_dist': {
            'pythons': (__file__, ['2.7', '3.6', '3.7']),
            'platforms': (__file__, 'all'),
        },
    },
)
