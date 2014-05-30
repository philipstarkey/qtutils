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
        # it matters whether they hold the gtk lock, and we'll either
        # have deadlocks when they already do, or have to have calling
        # code peppered with lock acquisitions. Screw that.
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
    
    # I think if we don't wait for the function to run in the main thread, then
    # we might avoid a backlog of messages when printing large amounts (eg in lyse)
    # It might just transfer the backlog to a queue of functions to be executed in 
    # the main thread, so perhaps it makes no difference!
    @inmain_decorator(False) 
    def add_text(self,text,red):
        if self.scrollbar.value() == self.scrollbar.maximum():
            self.scroll_to_end = True
        else:
            self.scroll_to_end = False
    
        cursor = self.output_textedit.textCursor()
        cursor.movePosition(QTextCursor.End)
        if red:
            cursor.insertHtml('<p style="font-family:\'Courier New\'"><font color="red"><b>%s<br/></b></font></p>'%text.replace(' ','&nbsp;').replace('\n','<br/>'))
        else:
            cursor.insertHtml('<p style="font-family:\'Courier New\'"><font color="white"><b>%s<br/></b></font></p>'%text.replace(' ','&nbsp;').replace('\n','<br/>'))
        #cursor.insertBlock()
       
        if self.scroll_to_end:
            self.scrollbar.setValue(self.scrollbar.maximum())

if __name__ == '__main__':    
    import sys,os    
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)
    
    output_box = OutputBox(layout)
    output_box.output('some text')
    output_box.output('some text',True)
    output_box.output('Blah blah',True)
    output_box.output('The quick brown fox jumped over the lazy dog')
    output_box.output('The quick brown fox jumped over the lazy dog',True)
    
    output_box.output('some text')
    output_box.output('some text',True)
    output_box.output('Blah blah',True)
    output_box.output('The quick brown fox jumped over the lazy dog')
    output_box.output('The quick brown fox jumped over the lazy dog',True)
    
    output_box.output('some text')
    output_box.output('some text',True)
    output_box.output('Blah blah',True)
    output_box.output('The quick brown fox jumped over the lazy dog')
    output_box.output('The quick brown fox jumped over the lazy dog',True)
    
    def button_pushed(*args,**kwargs):
        global output_box
        output_box.output('More Text')
        print output_box.output_textedit.toHtml()
        
    button = QPushButton("push me")
    button.clicked.connect(button_pushed)
    layout.addWidget(button)
    
    window.show()
    def run():
        app.exec_()
        
    sys.exit(run())
