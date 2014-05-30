#!/usr/bin/env python

# To upload a version to PyPI, run:
#
#    python setup.py sdist upload
#
# If the package is not registered with PyPI yet, do so with:
#
# python setup.py register

from distutils.core import setup
import os

VERSION = '1.2.1'

# Auto generate a __version__ package for the package to import
with open(os.path.join('qtutils', '__version__.py'), 'w') as f:
    f.write("__version__ = '%s'\n"%VERSION)
    
setup(name='qtutils',
      version=VERSION,
      description='Utilities for providing concurrent access to Qt objects, simplified QSettings storage, and dynamic widget promotion when loading UI files, in Python Qt applications.',
      author='Philip Starkey',
      author_email='threepineapples@gmail.com',
      url='https://bitbucket.org/philipstarkey/qtutils',
      license="2-clause BSD, 3-clause BSD (see LICENSE.TXT for full conditions)",
      packages=['qtutils'],
     )
