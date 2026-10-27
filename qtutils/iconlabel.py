#####################################################################
#                                                                   #
# iconlabel.py                                                      #
#                                                                   #
# Copyright 2026, Christopher Billington, Philip Starkey            #
#                                                                   #
# This file is part of the qtutils project                          #
# (see https://github.com/philipstarkey/qtutils )                   #
# and is licensed under the 2-clause, or 3-clause, BSD License.     #
# See the license.txt file in the root of the project               #
# for the full license.                                             #
#                                                                   #
#####################################################################

from qtutils.qt.QtCore import *
from qtutils.qt.QtGui import *
from qtutils.qt.QtWidgets import *


class IconLabel(QWidget):
    """A widget that displays a QIcon, in place of a QLabel with a pixmap. The icon is
    painted from the QIcon each time, so it is drawn from the image for the screen that
    the widget is on. The icon is drawn in Disabled mode when the widget is disabled."""

    def __init__(self, parent=None, icon=None):
        super().__init__(parent)
        self._icon = QIcon()
        self._icon_size = None
        if icon is not None:
            self.setIcon(icon)

    def icon(self):
        return self._icon

    def setIcon(self, icon):
        self._icon = QIcon(icon)
        self.update()

    def iconSize(self):
        """The size at which the icon is drawn: the style's small icon size unless
        setIconSize() has been called."""
        if self._icon_size is not None:
            return self._icon_size
        extent = self.style().pixelMetric(QStyle.PM_SmallIconSize, None, self)
        return QSize(extent, extent)

    def setIconSize(self, size):
        self._icon_size = QSize(size)
        self.updateGeometry()
        self.update()

    def sizeHint(self):
        return self.iconSize()

    def minimumSizeHint(self):
        return self.iconSize()

    def paintEvent(self, event):
        painter = QPainter(self)
        mode = QIcon.Normal if self.isEnabled() else QIcon.Disabled
        rect = QStyle.alignedRect(
            self.layoutDirection(), Qt.AlignCenter, self.iconSize(), self.rect()
        )
        self._icon.paint(painter, rect, Qt.AlignCenter, mode)
