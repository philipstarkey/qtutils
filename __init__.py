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

from invoke_in_main import inmain, inmain_later, in_qt_thread, inmain_decorator

from qsettings_wrapper import QSettingsWrapper
from UiLoader import UiLoader

