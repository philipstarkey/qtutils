#####################################################################
#                                                                   #
# outputbox.py                                                      #
#                                                                   #
# Copyright 2013, Christopher Billington, Philip Starkey            #
#                                                                   #
# This file is part of the qtutils project                          #
# (see https://bitbucket.org/philipstarkey/qtutils )                #
# and is licensed under the 2-clause, or 3-clause, BSD License.     #
# See the license.txt file in the root of the project               #
# for the full license.                                             #
#                                                                   #
#####################################################################

from __future__ import division, unicode_literals, print_function, absolute_import
import sys
PY2 = sys.version_info[0] == 2
if PY2:
    chr = unichr

import threading

from qtutils.qt.QtCore import *
from qtutils.qt.QtGui import *
from qtutils.qt.QtWidgets import *

import zmq
from qtutils.auto_scroll_to_end import set_auto_scroll_to_end
from qtutils import *
import ast

    
# This should cover most platforms:
acceptable_fonts = ["Ubuntu mono",
                    "Courier 10 Pitch",
                    "Courier Std",
                    "Consolas",
                    "Courier",
                    "FreeMono",
                    "Nimbus Mono L",
                    "Courier New",
                    "monospace"]


GREY = GRAY = '#75715E' 
BACKGROUND = '#141411'
WHITE = '#FFFFFF'
RED = '#EF2020'
ORANGE = '#FD971F'
YELLOW = '#FCE94F'
GREEN = '#A6E22E'
BLUE = '#66D9EF'
PURPLE = '#AE81FF'


_charformats = {}

def charformats(charformat_repr):
    try:
        return _charformats[charformat_repr]
    except KeyError:
        pass
    try:
        color, bold, italic = ast.literal_eval(charformat_repr)
    except Exception:
        if charformat_repr == 'stderr':
            color, bold, italic = 'red', False, False
        else:
            # stdout, or invalid spec. Use plain font:
            color, bold, italic = WHITE, False, False
    try:
        qcolor = QColor(color)
    except Exception:
        # invalid color, use white:
        qcolor = QColor(WHITE)
    font = QFont("SomeMonoFont", 11)
    font.insertSubstitutions("SomeMonoFont", acceptable_fonts)
    font.setBold(bold)
    font.setItalic(italic)
    fmt = QTextCharFormat()
    fmt.setForeground(QBrush(qcolor))
    fmt.setFont(font)
    _charformats[color, bold, italic] = fmt
    return fmt


class OutputBox(object):

    def __init__(self, container, scrollback_lines=1000):
        self.output_textedit = QPlainTextEdit()
        container.addWidget(self.output_textedit)
        self.output_textedit.setReadOnly(True)
        palette = self.output_textedit.palette()
        palette.setColor(QPalette.Base, QColor(BACKGROUND))
        self.output_textedit.setPalette(palette)

        self.output_textedit.setBackgroundVisible(False)
        self.output_textedit.setWordWrapMode(QTextOption.WrapAnywhere)
        set_auto_scroll_to_end(self.output_textedit.verticalScrollBar())
        self.output_textedit.setMaximumBlockCount(scrollback_lines)

        # Keeping track of whether the output is in the middle of a line
        # or not:
        self.mid_line = False

        context = zmq.Context.instance()
        socket = context.socket(zmq.PULL)
        socket.setsockopt(zmq.LINGER, 0)

        self.port = socket.bind_to_random_port('tcp://127.0.0.1')

        # Thread-local storage so we can have one push_sock per thread.
        # push_sock is for sending data to the output queue in a non-blocking
        # way from the same process as this object is instantiated in.
        # Providing the function OutputBox.output() for this is much easier
        # than expecting every thread to have its own push socket that the
        # user has to manage. Also we can't give callers direct access to the
        # output code, because then it matters whether they're in the GUI main
        # thread or not. We could decorate it with inmain_decorator, but it is
        # still useful for the all threads and processed to send to the same
        # zmq socket - it keeps messages in order, nobody 'jumps the queue' so
        # to speak.
        self.local = threading.local()

        self.mainloop = threading.Thread(target=self.mainloop, args=(socket,))
        self.mainloop.daemon = True
        self.mainloop.start()

    def new_socket(self):
        # One socket per thread, so we don't have to acquire a lock
        # to send:
        context = zmq.Context.instance()
        self.local.push_sock = context.socket(zmq.PUSH)
        self.local.push_sock.connect('tcp://127.0.0.1:%d' % self.port)

    def write(self, text, color=WHITE, bold=False, italic=False):
        """Write to the output box as if it were a file. Takes a string as
        does not append newlines or anything else. use OutputBox.print() for
        an interface more like the Python print() function."""
        if not hasattr(self.local, 'push_sock'):
            self.new_socket()
        # Queue the output on the socket:
        charformat = repr((color, bold, italic)).encode('utf8')
        self.local.push_sock.send_multipart([charformat, text.encode('utf8')])

    def print(self, *values, **kwargs):
        """Print to the output box. This method accepts the same arguments as
        the Python print function. If file=sys.stderr, the output will be red
        and bold. If it is absent or sys.stdout, it will be white. Anything
        else is an exception. The 'color' and 'bold' keyword arguments if
        provided will override the settings inferred from the file keyword
        argument."""

        sep = kwargs.pop('sep', None)
        end = kwargs.pop('end', None)
        file = kwargs.pop('file', None)

        if sep is None:
            sep = ' '
        if end is None:
            end = '\n'
        if file is None:
            file = sys.stdout

        

        if file is sys.stdout:
            color = WHITE
            bold = False
        elif file is sys.stderr:
            color = 'red'
            bold = False
        else:
            msg = 'file argument for OutputBox.print() must be stdout or stderr'
            raise ValueError(msg)
        bold = kwargs.pop('bold', bold)
        color = kwargs.pop('color', color)
        italic = kwargs.pop('italic', False)
        self.write(sep.join(str(s) for s in values) + end, color=color, bold=bold, italic=italic)

    def output(self, text, red=False):
        """Wrapper around write() with only option for normal text or bold red
        text, retained for backward compatibility but deprecated."""
        if red:
            color = 'red'
            bold = False
        else:
            color = WHITE
            bold = False
        self.write(text, color=color, bold=bold)

    def mainloop(self, socket):
        while True:
            messages = []
            current_charformat = None
            # Wait for messages
            socket.poll()
            # Get all messages waiting in the pipe, concatenate strings to
            # reduce the number of times we call add_text (which requires posting
            # to the qt main thread, which can be a bottleneck when there is a lot of output)
            while True:
                try:
                    charformat_repr, text = socket.recv_multipart(zmq.NOBLOCK)
                except zmq.Again:
                    break
                if charformat_repr != current_charformat:
                    current_charformat = charformat_repr
                    current_message = []
                    messages.append((current_charformat, current_message))
                current_message.append(text)
            for charformat_repr, message in messages:
                text = b''.join(message).decode('utf8')
                self.add_text(text, charformat_repr.decode('utf8'))

    @inmain_decorator(True)
    def add_text(self, text, charformat_repr):
        # The convoluted logic below is because we want a few things that
        # conflict slightly. Firstly, we want to take advantage of our
        # setMaximumBlockCount setting; Qt will automatically remove old
        # lines, but only if each line is a separate 'block'. So each line has
        # to be inserted with appendPlainText - this appends a new block.
        # However, we also want to support partial lines coming in, and we
        # want to print that partial line without waiting until we have the
        # full line. So we keep track (with the instance variable
        # self.mid_line) whether we are in the middle of a line or not, and if
        # we are we call insertText, which does *not* start a new block.
        cursor = self.output_textedit.textCursor()
        lines = text.split('\n')
        if self.mid_line:
            first_line = lines.pop(0)
            cursor = self.output_textedit.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(first_line)
        for line in lines[:-1]:
            self.output_textedit.appendPlainText(line)
        if lines:
            last_line = lines[-1]
            if last_line:
                self.output_textedit.appendPlainText(last_line)
                self.mid_line = True
            else:
                self.mid_line = False

        n_chars_printed = len(text)
        if not self.mid_line:
            n_chars_printed -= 1  # Because we didn't print the final newline character
        cursor.movePosition(QTextCursor.End)
        cursor.movePosition(QTextCursor.PreviousCharacter, n=n_chars_printed)
        cursor.movePosition(QTextCursor.End, mode=QTextCursor.KeepAnchor)
        cursor.setCharFormat(charformats(charformat_repr))


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)

    output_box = OutputBox(layout)

    for i in range(3):
        output_box.write('white, two line breaks.\n\n')
        output_box.write('white, no linebreak.')
        output_box.write('Red.\n', color='red')
        output_box.output('Red with the deprecated function.\n', red=True)
        output_box.write('More red, also bold.\n', color='red', bold=True)
        output_box.write('The \"quick white fox\" jumped over the \'lazy\' dog\n')
        output_box.write('<The bold, green, italic fox jumped over the lazy dog>\n', color=GREEN, bold=True, italic=True)
        output_box.write(b'Der schnelle braune Fuchs ist \xc3\xbcber den faulen Hund gesprungen\n'.decode('utf8'))

        output_box.print("print test")
        output_box.print("stderr", "test", 123, file=sys.stderr)

        output_box.print()

    for i in range(3):
        output_box.print('This is just some info from runmanager in bold blue', bold=True, italic=True, color=BLUE)
        output_box.print('Some more info in a subdued grey', italic=True, color=GREY)

    for i in range(2):
        output_box.print('\nthis is runmanager running your script in purple', color=PURPLE)
        for j in range(5):
            output_box.print('The \"quick white fox\" jumped over the \'lazy\' dog')
        if i:
            output_box.print("RunTimeError('your script broke')", file=sys.stderr)
            output_box.print('it failed in bold red', color=RED, bold=True, italic=True)
        else:
            output_box.print("Your script worked fine")
            output_box.print('it worked in green', color=GREEN, italic=True)
            output_box.print('submitting to BLACS in yellow...', color=YELLOW, italic=True, end='')
            output_box.print('success in bold green', color=GREEN, bold=True, italic=True)
            output_box.print('warning: queue is paused in orange', color=ORANGE, italic=True)
            

    def button_pushed(*args, **kwargs):
        import random
        uchars = [random.randint(0x20, 0x7e) for _ in range(random.randint(0, 50))]
        ustr = u''
        for uc in uchars:
            ustr += chr(uc)
        red = random.randint(0, 1)
        newline = random.randint(0, 1)
        hex = __builtins__.hex
        color = '#' + hex(random.randint(0, 0xffffff))[2:]
        bold = random.randint(0, 1)
        italic = random.randint(0, 1)
        output_box.write(ustr + ('\n' if newline else ''), color=color, bold=bold, italic=italic)

    button = QPushButton("push me to output random text")
    button.clicked.connect(button_pushed)
    layout.addWidget(button)

    window.show()
    window.resize(500, 500)

    def run():
        app.exec_()

    sys.exit(run())
