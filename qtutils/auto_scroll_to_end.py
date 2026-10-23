import sys
import weakref

from qtutils.qt.QtCore import *
from qtutils.qt.QtGui import *
from qtutils.qt.QtWidgets import *

_auto_scrollers = weakref.WeakKeyDictionary()


class _AutoScroller(QObject):
    def __init__(self, scrollbar):
        super().__init__(scrollbar)
        # The widget whose visibility we check. A scrollbar with the 'as needed' policy
        # is hidden when its range is empty, so we use the scroll area that contains it.
        self.scroll_area = scrollbar
        parent = scrollbar.parentWidget()
        while parent is not None:
            if isinstance(parent, QAbstractScrollArea):
                self.scroll_area = parent
                break
            parent = parent.parentWidget()
        self.at_end = scrollbar.value() == scrollbar.maximum()
        self.at_end_when_shown = False
        # Qt widgets can change the scrollbar value when they are shown, for example
        # QPlainTextEdit scrolls to its text cursor if text was appended while it was
        # hidden. We restore the position at the end once the show event and the
        # layout changes that it triggers have been processed:
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(0)
        self.timer.timeout.connect(self.on_shown)
        scrollbar.valueChanged.connect(self.on_value_changed)
        scrollbar.rangeChanged.connect(self.on_range_changed)
        self.scroll_area.installEventFilter(self)

    def on_value_changed(self, value):
        # Qt changes the value of a hidden scrollbar when it lays out content or removes
        # lines from the start of a QPlainTextEdit. We ignore these changes.
        if self.scroll_area.isVisible():
            self.at_end = value == self.parent().maximum()

    def on_range_changed(self, minval, maxval):
        if self.at_end:
            self.parent().setValue(maxval)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Show:
            self.at_end_when_shown = self.at_end
            self.timer.start()
        return False

    def on_shown(self):
        if self.at_end_when_shown:
            scrollbar = self.parent()
            scrollbar.setValue(scrollbar.maximum())
            self.at_end = True

    def remove(self):
        self.timer.stop()
        self.scroll_area.removeEventFilter(self)
        scrollbar = self.parent()
        scrollbar.valueChanged.disconnect(self.on_value_changed)
        scrollbar.rangeChanged.disconnect(self.on_range_changed)
        self.setParent(None)


def set_auto_scroll_to_end(scrollbar):
    """Configures any scrollbar to always scroll to the end when its range is increased,
    if it was already scrolled to the end before the range increased. Whether the
    scrollbar is at the end is recorded only while it is visible, and is restored when
    it is shown."""
    _auto_scrollers[scrollbar] = _AutoScroller(scrollbar)


def unset_auto_scroll_to_end(scrollbar):
    _auto_scrollers.pop(scrollbar).remove()


if __name__ == '__main__':
    # test. Should auto scroll to the bottom until the
    # 50th item, and then not auto scroll any more.
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)
    view = QListView(window)
    model = QStandardItemModel()
    view.setModel(model)
    layout.addWidget(view)

    window.show()
    window.resize(200, 200)

    i = 0

    def add_line():
        global i
        model.appendRow(QStandardItem(str(i)))
        i += 1
        if i == 50:
            unset_auto_scroll_to_end(view.verticalScrollBar())

    timer = QTimer()
    timer.timeout.connect(add_line)
    timer.start(100)

    set_auto_scroll_to_end(view.verticalScrollBar())
    app.exec_()
