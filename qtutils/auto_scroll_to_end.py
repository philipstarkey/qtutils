from __future__ import division, unicode_literals, print_function, absolute_import
import sys
PY2 = sys.version_info[0] == 2
if PY2:
    str = unicode
import weakref

from qtutils.qt.QtCore import *
from qtutils.qt.QtGui import *
from qtutils.qt.QtWidgets import *

# These are weakref dictionarys so that we do not hold references
# to the scrollbars after nobody else does:
_is_scrolled_to_bottom = weakref.WeakKeyDictionary()
_callbacks = weakref.WeakKeyDictionary()


def set_auto_scroll_to_end(scrollbar):
    """Configures any scrollbar to always  scroll to the end when its range is increased,
    if it was already scrolled to the end before the range increased."""

    def on_scrollbar_value_changed(value=None):
        if scrollbar.value() == scrollbar.maximum():
            _is_scrolled_to_bottom[scrollbar] = True
        else:
            _is_scrolled_to_bottom[scrollbar] = False

    def on_scrollbar_range_changed(minval, maxval):
        if _is_scrolled_to_bottom[scrollbar]:
            scrollbar.setValue(maxval)

    scrollbar.valueChanged.connect(on_scrollbar_value_changed)
    scrollbar.rangeChanged.connect(on_scrollbar_range_changed)
    # Call this to add the scrollbar to the dictionary and store whether it is initially at the end or not:
    on_scrollbar_value_changed(scrollbar)
    # Store the callbacks for disconnection:
    _callbacks[scrollbar] = on_scrollbar_value_changed, on_scrollbar_range_changed


def unset_auto_scroll_to_end(scrollbar):
    on_scrollbar_value_changed, on_scrollbar_range_changed = _callbacks[scrollbar]
    scrollbar.valueChanged.disconnect(on_scrollbar_value_changed)
    scrollbar.rangeChanged.disconnect(on_scrollbar_range_changed)


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
