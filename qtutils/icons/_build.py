from __future__ import division, unicode_literals, print_function, absolute_import

import os
import subprocess

this_folder = os.path.dirname(os.path.realpath(__file__))
qrc_filename = os.path.join(this_folder, 'icons.qrc')
py_filename_pyqt5 = os.path.join(this_folder, '_icons_pyqt5.py')
py_filename_pyqt4 = os.path.join(this_folder, '_icons_pyqt4.py')
py_filename_pyside = os.path.join(this_folder, '_icons_pyside.py')
icon_folders = ['custom', 'fugue']


def make_qrc_file():
    header = "<!DOCTYPE RCC><RCC version=\"1.0\">\n    <qresource  prefix=\"/qtutils\">\n"
    footer = "    </qresource>\n</RCC>"
    line_format_string = "     <file>%s</file>\n"
    with open(qrc_filename, 'w') as outfile:
        outfile.write(header)
        for folder in icon_folders:
            for filename in os.listdir(os.path.join(this_folder, folder)):
                relative_path = '%s/%s' % (folder, filename)  # Has to be forward slash, not system specific path separator
                outfile.write(line_format_string % relative_path)
        outfile.write(footer)


def find_pyrcc5():
    import PyQt5
    # If we're on Windows, it's probably in the pyqt4 directory:
    if os.name == 'nt':
        pyqt5_dir = os.path.abspath(os.path.dirname(PyQt5.__file__))
        pyrcc5 = os.path.join(pyqt5_dir, 'pyrcc5.exe')
        if os.path.exists(pyrcc5):
            return pyrcc5
    # Otherwise, or if it was not found there, check if it's in the PATH:
    pyrcc5 = 'pyrcc5'
    try:
        subprocess.call([pyrcc5], stdout=open(os.devnull), stderr=open(os.devnull))
        return pyrcc5
    except OSError:
        # Still no?
        msg = """
                Cannot find pyrcc5, the PyQt5 utility for building resource
                files. This module was configured to find it in the PyQt5
                directory on Windows, which is where it is for the Anaconda
                Python distribution. This module should also find pyrcc5 if it
                in in the PATH, on any OS. Please find pyrcc5 and put it in your
                PATH. On Debian based systems it is available in the pyqt5-dev-
                tools package. If you want to install qtutils without PyQt5
                support, simply run:
                python setup.py install NO_PYQT5"""
        import textwrap
        raise OSError(textwrap.dedent(msg).strip())


def find_pyrcc4():
    import PyQt4
    # If we're on Windows, it's probably in the pyqt4 directory:
    if os.name == 'nt':
        pyqt4_dir = os.path.abspath(os.path.dirname(PyQt4.__file__))
        pyrcc4 = os.path.join(pyqt4_dir, 'pyrcc4.exe')
        if os.path.exists(pyrcc4):
            return pyrcc4
    # Otherwise, or if it was not found there, check if it's in the PATH:
    pyrcc4 = 'pyrcc4'
    try:
        subprocess.call([pyrcc4], stdout=open(os.devnull), stderr=open(os.devnull))
        return pyrcc4
    except OSError:
        # Still no?
        msg = """
              Cannot find pyrcc4, the PyQt4 utility for building resource
              files. This module was configured to find it in the PyQt4
              directory on Windows, which is where it is for the Anaconda
              Python distribution. This module should also find pyrcc4 if it
              in in the PATH, on any OS. Please find pyrcc4 and put it in your
              PATH. On Debian based systems it is available in the pyqt4-dev-
              tools package. If you want to install qtutils without PyQt4
              support, simply run:
              python setup.py install NO_PYQT4"""
        import textwrap
        raise OSError(textwrap.dedent(msg).strip())


def find_pyside_rcc():
    import PySide
    # If we're on Windows, it's probably in the PySide directory:
    if os.name == 'nt':
        pyside_dir = os.path.abspath(os.path.dirname(PySide.__file__))
        pyside_rcc = os.path.join(pyside_dir, 'pyside-rcc.exe')
        if os.path.exists(pyside_rcc):
            return pyside_rcc
    # Otherwise, or if it was not found there, check if it's in the PATH:
    pyside_rcc = 'pyside-rcc'
    try:
        subprocess.call([pyside_rcc], stdout=open(os.devnull), stderr=open(os.devnull))
        return pyside_rcc
    except OSError:
        # Still no?
        msg = """
              Cannot find pyside-rcc, the PySide utility for building
              resource files. This module was configured to find it in the
              PySide directory on Windows, which is where it is for the
              Anaconda Python distribution. This module should also find
              pyside-rcc if it in in the PATH, on any OS. Please find pyside-
              rcc and put it in your PATH. On Debian based systems it is
              available in the pyqt4-dev- tools package. If you want to
              install qtutils without PySide support, simply run:
              python setup.py install NO_PYSIDE"""
        import textwrap
        raise OSError(textwrap.dedent(msg).strip())


def make_py_file_pyqt5():
    pyrcc5 = find_pyrcc5()
    child = subprocess.Popen([pyrcc5, '-o', py_filename_pyqt5, qrc_filename])
    stdoutdata, stderrdata = child.communicate()
    if child.returncode != 0:
        raise OSError(stderrdata)


def make_py_file_pyqt4():
    pyrcc4 = find_pyrcc4()
    child = subprocess.Popen([pyrcc4, '-py3', '-o', py_filename_pyqt4, qrc_filename])
    stdoutdata, stderrdata = child.communicate()
    if child.returncode != 0:
        raise OSError(stderrdata)


def make_py_file_pyside():
    pyside_rcc = find_pyside_rcc()
    child = subprocess.Popen([pyside_rcc, '-py3', '-o', py_filename_pyside, qrc_filename])
    stdoutdata, stderrdata = child.communicate()
    if child.returncode != 0:
        raise OSError(stderrdata)


def pyqt5():
    if not os.path.exists(py_filename_pyqt5):
        make_py_file_pyqt5()


def pyqt4():
    if not os.path.exists(py_filename_pyqt4):
        make_py_file_pyqt4()


def pyside():
    if not os.path.exists(py_filename_pyside):
        make_py_file_pyside()


if not os.path.exists(qrc_filename):
    make_qrc_file()
