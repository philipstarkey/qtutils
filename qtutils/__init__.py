#####################################################################
#                                                                   #
# __init__.py                                                       #
#                                                                   #
# Copyright 2013, Christopher Billington, Philip Starkey            #
#                                                                   #
# This file is part of the qtutils project                          #
# (see https://github.com/philipstarkey/qtutils )                   #
# and is licensed under the 2-clause, or 3-clause, BSD License.     #
# See the license.txt file in the root of the project               #
# for the full license.                                             #
#                                                                   #
#####################################################################
import os

from .__version__ import __version__
from qtutils.qt.QtCore import qInstallMessageHandler
from qtutils.locking import qtlock

if os.getenv('QTUTILS_ENFORCE_QTLOCK', '') not in ('', '0'):
    qtlock.enforce()

from qtutils.invoke_in_main import inmain, inmain_later, inthread, inmain_decorator

from qtutils.qsettings_wrapper import QSettingsWrapper
from qtutils.disconnect_contextmanager import DisconnectContextManager
from qtutils.UiLoader import UiLoader
