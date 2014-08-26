#####################################################################
#                                                                   #
# disconnect_contextmanager.py                                                       #
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

import sys
if 'PySide' in sys.modules:
    from PySide.QtCore import *
else:
    from PyQt4.QtCore import *
    
class DisconnectContextManager(object):
    def __init__(self, signal, slot):
        self.signal = signal
        self.slot = slot
    def __enter__(self):
        self.signal.disconnect(self.slot)
    def __exit__(self, *exc_info):
        self.signal.connect(self.slot)
        