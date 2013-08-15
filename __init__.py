from PySide.QtCore import qInstallMsgHandler 

def _message_handler(type, message):
    """Handle qt warnings etc with an exception, so they don't pass
    unnoticed"""
    print '%s: %s'%(type,message)
    #raise Exception('%s: %s'%(type,message))
        
qInstallMsgHandler(_message_handler)
del qInstallMsgHandler

from locking import qtlock
qtlock.enforce()

from invoke_in_main import inmain, inmain_later, inthread, inmain_decorator

from UiLoader import loadUi

