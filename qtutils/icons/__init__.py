import os
import subprocess
import PyQt4

this_folder = os.path.dirname(os.path.realpath(__file__))
qrc_filename = os.path.join(this_folder, 'icons.qrc')
py_filename = os.path.join(this_folder, '_icons.py')
icon_folders = ['custom', 'fugue']

def make_qrc_file():
    header = "<!DOCTYPE RCC><RCC version=\"1.0\">\n    <qresource>\n"
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
    # If we're on Windows, it's probably in the pyqt4 directory:
    if os.name == 'nt':
        pyqt4_dir = os.path.abspath(os.path.dirname(PyQt4.__file__))
        pyrcc4 = os.path.join(pyqt4_dir, 'pyrcc4.exe')
        if os.path.exists(pyrcc4):
            return pyrcc4
    # Otherwise, or if it was not found there, check if it's in the PATH:
    pyrcc4 = 'pyrcc4'
    try:
        subprocess.call([pyrcc4])
        return pyrcc4
    except OsError:
        # Still no?
        msg = ('Cannot find pyrcc4, the Qt utility for building resource files. ' + 
              'This module was configured to find it in the PyQt4 directory on Windows, ' +
              'which is where it is for the Anaconda Python distribution. This module ' +
              'should also find pyrcc4 if it in in the PATH, on any OS. Please find pyrcc4 ' +
              'and put it in your PATH, or modify this module\'s find_pyrcc4() function to ' + 
              'also search in the location that pyrcc4 resides on your system. ' +
              'Please also report a bug to the labscript project so we can fix it!')
        raise OSError(msg)

        
def make_py_file():
    pyrcc4 = find_pyrcc4()
    child = subprocess.Popen([pyrcc4, '-py3', '-o', py_filename, qrc_filename])
    stdoutdata, stderrdata = child.communicate()
    if child.returncode != 0:
        raise OSError(stderrdata)
        
if not os.path.exists(qrc_filename):
    make_qrc_file()
if not os.path.exists(py_filename):    
    make_py_file()

# Once the files exist, import the newly created module to register the resources with PyQt.
# PyQt code will then be able to access the icons.
import qtutils.icons._icons