#!/usr/bin/env python

# To upload a version to PyPI, run:
#
#    python setup.py sdist upload
#
# If the package is not registered with PyPI yet, do so with:
#
# python setup.py register

from __future__ import absolute_import, print_function
from distutils.core import setup
import sys
import os

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

VERSION = '2.2.3'

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

setup(name='qtutils',
      version=VERSION,
      description='Utilities for providing concurrent access to Qt objects, simplified QSettings storage, and dynamic widget promotion when loading UI files, in Python Qt applications. Also includes the Fugue icon set, by Yusuke Kamiyamane',
      author='Philip Starkey',
      author_email='threepineapples@gmail.com',
      url='https://bitbucket.org/philipstarkey/qtutils',
      license="2-clause BSD, 3-clause BSD (see LICENSE.TXT for full conditions)",
      packages=['qtutils', 'qtutils.icons'],
      package_data={'qtutils.icons':
                    ['custom/*',
                     'fugue/*',
                     'icons.qrc',
                     'README.txt'],
                     'qtutils':
                    ['fonts/*']}
      )
