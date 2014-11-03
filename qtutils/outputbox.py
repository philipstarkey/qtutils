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

from __future__ import print_function
import threading
import sys

if 'PySide' in sys.modules:
    from PySide.QtCore import *
    from PySide.QtGui import *
else:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

import zmq
from qtutils.auto_scroll_to_end import set_auto_scroll_to_end
from qtutils import *

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


class OutputBox(object):

    def __init__(self, container, scrollback_lines=1000):
        self.output_textedit = QPlainTextEdit()
        container.addWidget(self.output_textedit)
        self.output_textedit.setReadOnly(True)
        palette = self.output_textedit.palette()
        palette.setColor(QPalette.Base, QColor('black'))
        self.output_textedit.setPalette(palette)

        self.output_textedit.setBackgroundVisible(False)
        self.output_textedit.setWordWrapMode(QTextOption.WrapAnywhere)
        set_auto_scroll_to_end(self.output_textedit.verticalScrollBar())
        self.output_textedit.setMaximumBlockCount(scrollback_lines)

        # Keeping track of whether the output is in the middle of a line
        # or not:
        self.mid_line = False

        normal_font = QFont("SomeMonoFont", 11)
        normal_font.insertSubstitutions("SomeMonoFont", acceptable_fonts)
        self.normal_text_format = QTextCharFormat()
        self.normal_text_format.setForeground(QBrush(QColor('white')))
        self.normal_text_format.setFont(normal_font)

        red_font = QFont("SomeMonoFont", 11)
        red_font.insertSubstitutions("SomeMonoFont", acceptable_fonts)
        red_font.setBold(True)
        self.red_text_format = QTextCharFormat()
        self.red_text_format.setForeground(QBrush(QColor('red')))
        self.red_text_format.setFont(red_font)

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

    def output(self, text, red=False):
        if not hasattr(self.local, 'push_sock'):
            self.new_socket()
        # Queue the output on the socket:
        self.local.push_sock.send_multipart(['stderr' if red else 'stdout', text.encode('utf8')])

    def mainloop(self, socket):
        while True:
            messages = []
            current_stream = None
            # Wait for messages
            socket.poll()
            # Get all messages waiting in the pipe, concatenate strings to
            # reduce the number of times we call add_text (which requires posting
            # to the qt main thread, which can be a bottleneck when there is a lot of output)
            while True:
                try:
                    stream, text = socket.recv_multipart(zmq.NOBLOCK)
                except zmq.Again:
                    break
                if stream != current_stream:
                    current_stream = stream
                    current_message = []
                    messages.append((current_stream, current_message))
                current_message.append(text)
            for stream, message in messages:
                text = ''.join(message).decode('utf8')
                red = (stream == 'stderr')
                self.add_text(text, red)

    @inmain_decorator(True)
    def add_text(self, text, red):
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
        if red:
            cursor.setCharFormat(self.red_text_format)
        else:
            cursor.setCharFormat(self.normal_text_format)

            
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)

    output_box = OutputBox(layout)
    for i in range(3):
        output_box.output('white, two line breaks.\n\n')
        output_box.output('white, no linebreak.')
        output_box.output('Red.\n', True)
        output_box.output('More red.\n', True)
        output_box.output('The \"quick white fox\" jumped over the \'lazy\' dog\n')
        output_box.output('<The quick red fox jumped over the lazy dog>\n', True)
        output_box.output('Der schnelle braune Fuchs hat \xc3\xbcber den faulen Hund gesprungen\n'.decode('utf8'), True)

    def button_pushed(*args, **kwargs):
        import random
        uchars = [random.randint(0x20, 0x7e) for _ in range(random.randint(0, 50))]
        ustr = u''
        for uc in uchars:
            ustr += unichr(uc)
        red = random.randint(0, 1)
        newline = random.randint(0, 1)
        output_box.output(ustr + ('\n' if newline else ''), red=red)

    button = QPushButton("push me to output random text")
    button.clicked.connect(button_pushed)
    layout.addWidget(button)

    window.show()
    window.resize(500, 500)

    def run():
        app.exec_()

    sys.exit(run())
