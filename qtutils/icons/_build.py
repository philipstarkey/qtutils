import os
import subprocess

this_folder = os.path.dirname(os.path.realpath(__file__))
qrc_filename = os.path.join(this_folder, 'icons.qrc')
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
                relative_path = '%s/%s'%(folder, filename) # Has to be forward slash, not system specific path separator
                outfile.write(line_format_string%relative_path)      
        outfile.write(footer)
        
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
        msg = ('Cannot find pyrcc4, the PyQt4 utility for building resource files. ' + 
              'This module was configured to find it in the PyQt4 directory on Windows, ' +
              'which is where it is for the Anaconda Python distribution. This module ' +
              'should also find pyrcc4 if it in in the PATH, on any OS. Please find pyrcc4 ' +
              'and put it in your PATH, or modify this module\'s find_pyrcc4() function to ' + 
              'also search in the location that pyrcc4 resides on your system. ' +
              'Please also report a bug to the qtutils project so we can fix it! ' +
              'If you want to install qtutils without PyQt4 support, simply set ' +
              'BUILD_PYQT4_ICONS_RESOURCE = False in setup.py.')
        raise OSError(msg)

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
        msg = ('Cannot find pyside-rcc, the PySide utility for building resource files. ' + 
              'This module was configured to find it in the PySide directory on Windows, ' +
              'which is where it is for the Anaconda Python distribution. This module ' +
              'should also find pyside-rcc if it in in the PATH, on any OS. Please find pyside-rcc ' +
              'and put it in your PATH, or modify this module\'s find_pyside_rcc() function to ' + 
              'also search in the location that pyside-rcc resides on your system. ' +
              'Please also report a bug to the qtutils project so we can fix it! ' +
              'If you want to install qtutils without PySide support, simply set ' +
              'BUILD_PYSIDE_ICONS_RESOURCE = False in setup.py.')
        raise OSError(msg)
        
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
        
def pyqt4():
    if not os.path.exists(py_filename_pyqt4):    
        make_py_file_pyqt4()
        
def pyside():
    if not os.path.exists(py_filename_pyside):    
        make_py_file_pyside()

if not os.path.exists(qrc_filename):
    make_qrc_file()
