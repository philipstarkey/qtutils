#!/usr/bin/env python

# To upload a version to PyPI, run:
#
#    python setup.py sdist upload
#
# If the package is not registered with PyPI yet, do so with:
#
# python setup.py register

from distutils.core import setup

setup(name='qtutils',
      version='1.0.0',
      description='Utilities for providing concurrent access to Qt objects, simplified QSettings storage, and dynamic widget promotion when loading UI files, in Python Qt applications.',
      author='Philip Starkey',
      author_email='threepineapples@gmail.com',
      url='https://bitbucket.org/philipstarkey/qtutils',
      license="BSD",
      packages=['qtutils'],
      package_data={'qtutils': ['LICENSE.txt', 'README.md']}
     )
