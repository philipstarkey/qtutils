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
import cgi
from qtutils import qstring_to_unicode

if 'PySide' in sys.modules.copy():
    from PySide.QtCore import *
    from PySide.QtGui import *
else:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
    
import zmq
from qtutils import *

class OutputBox(object):
    def __init__(self, container, scrollback_lines=200):    
        self.output_textedit = QPlainTextEdit()
        container.addWidget(self.output_textedit)
        self.output_textedit.setReadOnly(True)
        # self.output_textedit.setStyleSheet("QPlainTextEdit { background-color: black}");
        self.scrollbar = self.output_textedit.verticalScrollBar()
        self.output_textedit.setMaximumBlockCount(scrollback_lines)
        
        # state to keep track of
        self.scroll_to_end = True 
        self.mid_line = False
        
        normal_text_format = QTextCharFormat()
        red_text_format = QTextCharFormat()
        
        context = zmq.Context.instance()
        socket = context.socket(zmq.PULL)
        socket.setsockopt(zmq.LINGER, 0)
        
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        
        self.port = socket.bind_to_random_port('tcp://127.0.0.1')
        
        # Tread-local storage so we can have one push_sock per
        # thread. push_sock is for sending data to the output queue in
        # a non-blocking way from the same process as this object is
        # instantiated in.  Providing the function OutputBox.output()
        # for this is much easier than expecting every thread to have
        # its own push socket that the user has to manage. Also we can't
        # give callers direct access to the output code, because then
        # it matters whether they're in the GUI main thread or not. We could
        # decorate it with inmain_decorator, but it is still useful for the
        # all threads and processed to send to the same zmq socket - it
        # keeps messages in order, nobody 'jumps the queue' so to speak.
        self.local = threading.local()
        
        self.mainloop = threading.Thread(target=self.mainloop, args=(socket, poller))
        self.mainloop.daemon = True
        self.mainloop.start()
    
    def new_socket(self):
        # One socket per thread, so we don't have to acquire a lock
        # to send:
        context = zmq.Context.instance()
        self.local.push_sock = context.socket(zmq.PUSH)
        self.local.push_sock.setsockopt(zmq.LINGER, 0)
        self.local.push_sock.connect('tcp://127.0.0.1:%d'%self.port)
        
    def output(self, text, red=False):
        if not hasattr(self.local, 'push_sock'):
            self.new_socket()
        # Queue the output on the socket:
        self.local.push_sock.send_multipart(['stderr' if red else 'stdout', text.encode('utf8')])
        
    def mainloop(self, socket, poller):
        while True:
            messages = []
            current_stream = None
            # Wait for messages
            poller.poll()
            while True:
                # Get all messages waiting in the pipe, concatenate strings to
                # reduce the number of times we call add_text (which requires posting
                # to the qt main thread, which can be a bottleneck when there is a lot of output
                try:
                    stream, text = socket.recv_multipart(zmq.NOBLOCK)
                except zmq.ZMQError:
                    break
                else:
                    if stream != current_stream:
                        current_stream = stream
                        current_message = []
                        messages.append((current_stream, current_message))
                    current_message.append(text)
            for stream, message in messages:
                message_text = ''.join(message).decode('utf8')
                red = (stream == 'stderr')
                self.add_text(message_text, red)
    
    @inmain_decorator(False) 
    def add_text(self, text, red):
        # self.output_textedit.setCurrentCharFormat()
        if self.scrollbar.value() == self.scrollbar.maximum():
            self.scroll_to_end = True
        else:
            print(self.scrollbar.maximum() == self.scrollbar.minimum())
            self.scroll_to_end = False
        
        # The convolution below is because we want to take advantage of 
        cursor = self.output_textedit.textCursor()
        lines = text.split('\n')
        if self.mid_line:
            first_line = lines.pop(0)
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
        if self.scroll_to_end:
            self.scrollbar.setValue(self.scrollbar.maximum())
                
if __name__ == '__main__':    
    import sys,os
    from qtutils import qstring_to_unicode
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)
    
    output_box = OutputBox(layout)
    for i in range(1):
        output_box.output('some text\n\n')
        output_box.output('some text')
        output_box.output('Fish & Chips\n', True)
        output_box.output('Blah blah\n', True)
        output_box.output('The \"quick brown fox\" jumped over the \'lazy\' dog\n')
        output_box.output('<The quick brown fox jumped over the lazy dog>\n', True)
        output_box.output('Der schnelle braune Fuchs springte \xc3\xbcber den faulen Hund\n'.decode('utf8'), True)
        
    def button_pushed(*args,**kwargs):
        output_box.output('More Text\n')
        
    button = QPushButton("push me")
    button.clicked.connect(button_pushed)
    layout.addWidget(button)
    
    i = 0
    def do_it():
        global i
        i += 1
        output_box.output('some text %d\n\n'%i)
        
    timer = QTimer()
    timer.timeout.connect(do_it)
    # timer.start(30)
    
    window.show()
    def run():
        app.exec_()
        
    sys.exit(run())
