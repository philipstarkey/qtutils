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

if 'PySide' in sys.modules.copy():
    from PySide.QtCore import *
    from PySide.QtGui import *
else:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
    
import zmq
from qtutils import *

class OutputBox(object):
    def __init__(self, container):    
        self.output_textedit = QTextEdit()
        container.addWidget(self.output_textedit)
        self.output_textedit.setReadOnly(True)
        self.output_textedit.setHtml("""<html><head></head><body bgcolor="#000000"></body></html>""")
        self.scrollbar = self.output_textedit.verticalScrollBar()
        self.scroll_to_end = True            
        
        context = zmq.Context.instance()
        socket = context.socket(zmq.PULL)
        socket.setsockopt(zmq.LINGER, 0)
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
        
        self.mainloop = threading.Thread(target=self.mainloop,args=(socket,))
        self.mainloop.daemon = True
        self.mainloop.start()
    
    def new_socket(self):
        # One socket per thread, so we don't have to acquire a lock
        # to send:
        context = zmq.Context.instance()
        self.local.push_sock = context.socket(zmq.PUSH)
        self.local.push_sock.setsockopt(zmq.LINGER, 0)
        self.local.push_sock.connect('tcp://127.0.0.1:%d'%self.port)
        
    def output(self, text,red=False):
        if not hasattr(self.local, 'push_sock'):
            self.new_socket()
        # Queue the output on the socket:
        self.local.push_sock.send_multipart(['stderr' if red else 'stdout',text.encode('utf8')])
        
    def mainloop(self,socket):
        while True:
            stream, text = socket.recv_multipart()
            text = text.decode('utf8')
            red = (stream == 'stderr')
            self.add_text(text,red)
    
    @inmain_decorator(False) 
    def add_text(self,text,red):
        if self.scrollbar.value() == self.scrollbar.maximum():
            self.scroll_to_end = True
        else:
            self.scroll_to_end = False
    
        cursor = self.output_textedit.textCursor()
        cursor.movePosition(QTextCursor.End)
        text = text.replace(' ','&nbsp;').replace('\n','<br>')
        cursor.insertHtml('<p style="font-family:\'Courier New\'">' +
                          '<font color="%s" size=4>'%('red' if red else 'white') + 
                          '<b>%s</b>'%text +
                          '</font></p>')
        #cursor.insertBlock()
       
        if self.scroll_to_end:
            self.scrollbar.setValue(self.scrollbar.maximum())

if __name__ == '__main__':    
    import sys,os    
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)
    
    output_box = OutputBox(layout)
    for i in range(3):
        output_box.output('some text\n')
        output_box.output('some text\n',True)
        output_box.output('Blah blah\n',True)
        output_box.output('The quick brown fox jumped over the lazy dog\n')
        output_box.output('The quick brown fox jumped over the lazy dog\n',True)
        
    def button_pushed(*args,**kwargs):
        global output_box
        output_box.output('More Text\n')
        print(output_box.output_textedit.toHtml())
        
    button = QPushButton("push me")
    button.clicked.connect(button_pushed)
    layout.addWidget(button)
    
    window.show()
    def run():
        app.exec_()
        
    sys.exit(run())
