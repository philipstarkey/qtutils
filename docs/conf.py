# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# Mock qt Library if necessary
# this is not really needed for RTD anymore, but seems to be useful for the
# restructured text preview extension in VS Code which doesn't seem to activate 
# the conda env properly and thus can't find the Qt DLL...
try:
    from qtutils.qt import QtGui, QtCore, QtWidgets
except Exception:
    print('Qt import failed, mocking PyQt5 and PySide6')
    import unittest.mock as mock 
    MOCK_MODULES = ['sip', 'PyQt5', 'PyQt5.QtGui', 'PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.uic', 'PySide6', 'PySide6.QtGui', 'PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtUiTools']
    sys.modules.update((mod_name, mock.MagicMock()) for mod_name in MOCK_MODULES)

from qtutils import __version__


# -- General configuration ------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'myst_parser',
]

templates_path = ['_templates']

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

master_doc = 'index'

project = u'qtutils'
copyright = u'2013, Christopher Billington, Philip Starkey'
author = u'Christopher Billington, Philip Starkey'

version = __version__
release = version

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'sphinx'


# -- Options for HTML output ----------------------------------------------

html_theme = 'sphinx_rtd_theme'


# -- Options for LaTeX output ---------------------------------------------

# (source start file, target name, title, author, documentclass)
latex_documents = [
    (master_doc, 'qtutils.tex', u'qtutils Documentation',
     u'Christopher Billington, Philip Starkey', 'manual'),
]
