#####################################################################
#                                                                   #
# __init__.py                                                       #
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

try:
    from __version__ import __version__
except ImportError:
    # Version file has not been autogenerated from build process:
    __version__ = None

import sys
if 'PySide' in sys.modules.copy():
    from PySide.QtCore import qInstallMsgHandler
else:
    try:
        from PyQt4.QtCore import qInstallMsgHandler
    except ImportError:
        from PyQt5.QtCore import qInstallMessageHandler as qInstallMsgHandler


def _message_handler(type, message):
    """Handle qt warnings etc with an exception, so they don't pass
    unnoticed"""
    print('%s: %s' % (type, message))
    #raise Exception('%s: %s'%(type,message))

qInstallMsgHandler(_message_handler)
del qInstallMsgHandler

from qtutils.locking import qtlock
qtlock.enforce()

from qtutils.invoke_in_main import inmain, inmain_later, inthread, inmain_decorator

from qtutils.qsettings_wrapper import QSettingsWrapper
from qtutils.disconnect_contextmanager import DisconnectContextManager
from qtutils.UiLoader import UiLoader
