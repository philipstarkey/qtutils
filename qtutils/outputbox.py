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
    import Queue as queue
else:
    import queue

import os
import threading

from qtutils.qt.QtCore import *
from qtutils.qt.QtGui import *
from qtutils.qt.QtWidgets import *

import zmq
from qtutils.auto_scroll_to_end import set_auto_scroll_to_end
from qtutils import *
import ast


if sys.platform == 'darwin':
    # Gotta make the font bigger on macOS for some reason:
    FONT_SIZE = 13
else:
    FONT_SIZE = 11

_fonts_initalised = False
_fonts_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')

def _add_fonts():
    """Add bundled fonts to the font database from file"""
    global _fonts_initalised
    for name in os.listdir(_fonts_folder):
        if name.endswith('.ttf'):
            path = os.path.join(_fonts_folder, name)
            QFontDatabase.addApplicationFont(path)
    _fonts_initalised = True

FONT = "Ubuntu Mono"

GREY = GRAY = '#75715E' 
BACKGROUND = '#141411'
WHITE = '#FFFFFF'
RED = '#EF2020'
ORANGE = '#FD971F'
YELLOW = '#FCE94F'
GREEN = '#A6E22E'
BLUE = '#66D9EF'
PURPLE = '#AE81FF'

FORMAT_ALIASES =  {
    'stdout': (WHITE, False, False),
    'stderr': (RED, False, False),
    'DEBUG': (GREY, False, False),
    'INFO': (BLUE, False, False),
    'WARNING': (YELLOW, True, False),
    'ERROR': (ORANGE, True, False),
    'CRITICAL': (RED, True, True)
}

_charformats = {}


def charformats(charformat_repr):
    try:
        return _charformats[charformat_repr]
    except KeyError:
        pass
    try:
        color, bold, italic = FORMAT_ALIASES[charformat_repr]
    except KeyError:
        # Not an alias
        try:
            color, bold, italic = ast.literal_eval(charformat_repr)
        except Exception:
            # Invalid spec. Use plain font:
            color, bold, italic = WHITE, False, False
    try:
        qcolor = QColor(color)
    except Exception:
        # invalid color, use white:
        qcolor = QColor(WHITE)

    if not _fonts_initalised:
        _add_fonts()

    font = QFont(FONT, FONT_SIZE)
    font.setBold(bold)
    font.setItalic(italic)
    fmt = QTextCharFormat()
    fmt.setForeground(QBrush(qcolor))
    fmt.setFont(font)
    _charformats[charformat_repr] = fmt
    return fmt


class OutputBox(object):

    # enum for keeping track of partial lines and carriage returns:
    LINE_START = 0
    LINE_MID = 1
    LINE_NEW = 2

    # Max number of lines to batch before printing to the GUI, to keep the GUI
    # responsive when lots of data comes in
    MAX_LINES_BATCH = 10

    # Declare that our write() method accepts a 'charformat' kwarg for specifying
    # formatting
    supports_rich_write = True

    def __init__(self, container, scrollback_lines=1000,
                 zmq_context=None, bind_address='tcp://127.0.0.1'):
        """Instantiate an outputBox and insert into container widget. Set the
        number of lines of scrollback to keep. Set a zmq_context for creating
        sockets, otherwise zmq.Context.instance() will be used. set
        bind_address, defaulting to the local interface."""
        self.output_textedit = QPlainTextEdit()
        container.addWidget(self.output_textedit)
        self.output_textedit.setReadOnly(True)
        palette = self.output_textedit.palette()
        palette.setColor(QPalette.Base, QColor(BACKGROUND))
        self.output_textedit.setPalette(palette)

        self.linepos = self.LINE_NEW
        self.output_textedit.setBackgroundVisible(False)
        self.output_textedit.setWordWrapMode(QTextOption.WrapAnywhere)
        set_auto_scroll_to_end(self.output_textedit.verticalScrollBar())
        self.output_textedit.setMaximumBlockCount(scrollback_lines)

        if zmq_context is None:
            zmq_context = zmq.Context.instance()
        self.zmq_context = zmq_context

        socket = self.zmq_context.socket(zmq.PULL)
        socket.setsockopt(zmq.LINGER, 0)

        self.port = socket.bind_to_random_port(bind_address)

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

        # A queue for text queued to be added to the box. The reason this is not passed
        # as an argument directly to self.add_text() is so that self.shutdown() can call
        # self.add_text repeatedly to synchronously finish adding pending text to the
        # box. Otherwise, one cannot shutdown in a race-free way that does not deadlock.
        self._text_queue = queue.Queue()

        self.shutting_down = False
        self.mainloop_thread = threading.Thread(target=self.mainloop, args=(socket,))
        self.mainloop_thread.daemon = True
        self.mainloop_thread.start()

    def new_socket(self):
        # One socket per thread, so we don't have to acquire a lock
        # to send:
        self.local.push_sock = self.zmq_context.socket(zmq.PUSH)
        self.local.push_sock.connect('tcp://127.0.0.1:%d' % self.port)

    def write(self, text, color=WHITE, bold=False, italic=False, charformat=None):
        """Write to the output box as if it were a file. Takes a string as does not
        append newlines or anything else. use OutputBox.print() for an interface more
        like the Python print() function. If charformat is provided, it will be used
        directly, otherwise the color, bold, and italic arguments will be used to
        determine the output format."""
        if not hasattr(self.local, 'push_sock'):
            self.new_socket()
        # Queue the output on the socket:
        if charformat is None:
            charformat = repr((color, bold, italic)).encode('utf8')
        elif isinstance(charformat, str):
            charformat = charformat.encode('utf8')
        self.local.push_sock.send_multipart([charformat, text.encode('utf8')])

    def print(self, *values, **kwargs):
        """Print to the output box. This method accepts the same arguments as the Python
        print function. If file=sys.stderr, the output will be red. If it is absent or
        sys.stdout, it will be white. Anything else is an exception. The 'color' and
        'bold' keyword arguments if provided will override the settings inferred from
        the file keyword argument."""

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
            color = RED
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
            color = RED
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
            n_lines = 0
            while True:
                try:
                    charformat_repr, text = socket.recv_multipart(zmq.NOBLOCK)
                    if text == b'shutdown' and self.shutting_down:
                        socket.close(linger=0)
                        return
                except zmq.Again:
                    break
                if charformat_repr != current_charformat:
                    current_charformat = charformat_repr
                    current_message = []
                    messages.append((current_charformat, current_message))
                current_message.append(text)
                n_lines += text.count(b'\n')
                if n_lines >= self.MAX_LINES_BATCH:
                    break
            for charformat_repr, message in messages:
                # Print non-character data with replacement sequences:
                text = b''.join(message).decode('utf8', errors='backslashreplace')
                try:
                    charformat_repr = charformat_repr.decode('utf8')
                except UnicodeDecodeError:
                    # Bad charformat repr. Ignore and print unformatted
                    charformat_repr = 'stdout'
                # Queue a call to self.add_text, and put the pending text in the queue
                # for it to consume. A separate queue is used so that a call to
                # self.shutdown() can call _add_text to add the remaining text
                # synchronously in order to make shutdown synchronous.
                self._text_queue.put((text, charformat_repr))
                self.add_text()

    @inmain_decorator(False)
    def add_text(self):
        try:
            text, charformat_repr = self._text_queue.get()
        except queue.Empty:
            # self.shutdown(), or some other additional calls to this method, have
            # beaten us to the punch. Nothing for us to do.
            return
        # The convoluted logic below is because we want a few things that conflict
        # slightly. Firstly, we want to take advantage of our setMaximumBlockCount
        # setting; Qt will automatically remove old lines, but only if each line is a
        # separate 'block'. So each line has to be inserted with appendPlainText - this
        # appends a new block. However, we also want to support partial lines coming in,
        # (and carraige returns! -LDT) and we want to print that partial line without
        # waiting until we have the full line. So we keep track (with the instance
        # variable self.linepos) whether we are at the start (post-CR), middle (no
        # termination of prev chunk) or end (got a '\n') of a line and if we are we at
        # start or middle we call insertText, which does *not* start a new block. LDT:
        # Note the handling of '\r' (CR) here is not *quite* what an actual teletype
        # would do, it returns to the start of the line but overwrites the whole line no
        # matter how much is printed, rather than only overwriting up to what new is
        # printed. I expect this difference not to matter too much!
        cursor = self.output_textedit.textCursor()
        lines = text.splitlines(True) # This keeps the line endings in the strings!
        cursor = self.output_textedit.textCursor()
        prevline_len = 0
        charsprinted = 0
        for line in lines:
            cursor.movePosition(QTextCursor.End)
            thisline = line.rstrip('\r\n') # Remove any of \r, \n or \r\n
            if self.linepos == self.LINE_START:    # Previous line ended in a carriage return. 
                cursor.movePosition(QTextCursor.StartOfBlock, mode=QTextCursor.KeepAnchor) # "Highlight" the text to be overwritten
                cursor.insertText(thisline)
                charsprinted -= prevline_len # We are replacing the previous line...
                prevline_len = len(thisline) # Reset the line length to this overwriting line
            elif self.linepos == self.LINE_MID:
                cursor.insertText(thisline)
                prevline_len += len(thisline)
            elif self.linepos == self.LINE_NEW:
                self.output_textedit.appendPlainText(thisline)
                charsprinted += 1  # Account for newline character here
                prevline_len = len(thisline)
            else:
                raise ValueError(self.linepos)
            charsprinted += len(thisline)
            # Set the line position for the next line, whenever that arrives
            if '\n' in line:
                self.linepos = self.LINE_NEW
            elif '\r' in line:
                self.linepos = self.LINE_START
            else:
                self.linepos = self.LINE_MID
            cursor.movePosition(QTextCursor.End)
            cursor.movePosition(QTextCursor.PreviousCharacter, n=charsprinted)
            cursor.movePosition(QTextCursor.End, mode=QTextCursor.KeepAnchor)
            cursor.setCharFormat(charformats(charformat_repr))
        
    def shutdown(self):
        """Stop the mainloop. Further writing to the OutputBox will be ignored. It is
        necessary to call this when done to prevent memory leaks, otherwise the mainloop
        thread will prevent the OutputBox from being garbage collected"""
        self.shutting_down = True
        self.write("shutdown")
        self.mainloop_thread.join()
        # Print queued text to the box until there is none left:
        while not self._text_queue.empty():
            self.add_text()
        self.shutting_down = False

    # Ensure instances can be treated as a file-like object:
    def close(self):
        pass

    def fileno(self):
        return 1

    def isatty(self):
        return False

    def flush(self):
        pass


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
    
    output_box.write("This sentence ends in a carriage return and should be overwritten and not be visible at all...\r")
    output_box.write("This should overwrite and then move on to the next line\n")

    output_box.print("This sentence is produced with print and ends in carriage return and should be overwritten and not be visible at all...",end="\r")
    output_box.print("This should overwrite with print and then move on to the next line")


    # Uncomment to test this. Requires zprocess:
    # import logging
    # from zprocess import RichStreamHandler, rich_print # Requires zprocess 2.5.1
    # logger = logging.Logger('test')
    # logger.setLevel(logging.DEBUG)
    # logger.addHandler(RichStreamHandler(output_box))
    # logger.debug('DEBUG log message')
    # logger.info('INFO log message')
    # logger.warning('WARNING log message')
    # logger.error('ERROR log message')
    # logger.critical('CRITICAL log message')
    # rich_print('green text via rich_print', color=GREEN, file=output_box)


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

    button2 = QPushButton("shutdown output box")
    button2.clicked.connect(output_box.shutdown)
    layout.addWidget(button2)


    window.show()
    window.resize(500, 500)

    def run():
        app.exec_()

    sys.exit(run())
