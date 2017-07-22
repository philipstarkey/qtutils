#####################################################################
#                                                                   #
# Qt.py                                                             #
#                                                                   #
# Copyright 2017, Jan Werkmann                                      #
#                                                                   #
# This file is part of the qtutils project                          #
# (see https://bitbucket.org/philipstarkey/qtutils )                #
# and is licensed under the 2-clause, or 3-clause, BSD License.     #
# See the license.txt file in the root of the project               #
# for the full license.                                             #
#                                                                   #
# The purpose of this wrapper is to provide a abstraction layer     #
# around the different versions of QtGui, QtCore and QtWidgets.     #
# The warpper is supposed to act like PyQt5, but might need         #
# addition in some cases.                                           #
#####################################################################

PYSIDE = 'PySide'
PYQT4 = 'PyQt4'
PYQT5 = 'PyQt5'

widget_names = ['QAbstractButton', 'QGraphicsAnchor', 'QMacCocoaViewContainer', 'QStyleOptionGroupBox', 'QAbstractGraphicsShapeItem', 'QGraphicsAnchorLayout', 'QMainWindow', 'QStyleOptionHeader', 'QAbstractItemDelegate', 'QGraphicsBlurEffect', 'QMdiArea', 'QStyleOptionMenuItem', 'QAbstractItemView', 'QGraphicsColorizeEffect', 'QMdiSubWindow', 'QStyleOptionProgressBar', 'QAbstractScrollArea', 'QGraphicsDropShadowEffect', 'QMenu', 'QStyleOptionRubberBand', 'QAbstractSlider', 'QGraphicsEffect', 'QMenuBar', 'QStyleOptionSizeGrip', 'QAbstractSpinBox', 'QGraphicsEllipseItem', 'QMessageBox', 'QStyleOptionSlider', 'QAction', 'QGraphicsGridLayout', 'QMouseEventTransition', 'QStyleOptionSpinBox', 'QActionGroup', 'QGraphicsItem', 'QOpenGLWidget', 'QStyleOptionTab', 'QApplication', 'GraphicsItemFlags', 'OptimizationFlags', 'QStyleOptionTabBarBase', 'AreaOptions', 'QGraphicsItemGroup', 'Options', 'QStyleOptionTabWidgetFrame', 'AutoFormatting', 'QGraphicsLayout', 'Options', 'QStyleOptionTitleBar', 'BlurHints', 'QGraphicsLayoutItem', 'QPanGesture', 'QStyleOptionToolBar', 'QBoxLayout', 'QGraphicsLineItem', 'QPinchGesture', 'QStyleOptionToolBox', 'ButtonFeatures', 'QGraphicsLinearLayout', 'QPlainTextDocumentLayout', 'QStyleOptionToolButton', 'QButtonGroup', 'QGraphicsObject', 'QPlainTextEdit', 'QStyleOptionViewItem', 'CacheMode', 'QGraphicsOpacityEffect', 'QProgressBar', 'QStylePainter', 'QCalendarWidget', 'QGraphicsPathItem', 'QProgressDialog', 'QStyledItemDelegate', 'ChangeFlags', 'QGraphicsPixmapItem', 'QProxyStyle', 'SubControls', 'ChangeFlags', 'QGraphicsPolygonItem', 'QPushButton', 'SubWindowOptions', 'QCheckBox', 'QGraphicsProxyWidget', 'QRadioButton', 'QSwipeGesture', 'QColorDialog', 'QGraphicsRectItem', 'RenderFlags', 'QSystemTrayIcon', 'ColorDialogOptions', 'QGraphicsRotation', 'Result', 'QTabBar', 'QColumnView', 'QGraphicsScale', 'QRubberBand', 'TabFeatures', 'QComboBox', 'QGraphicsScene', 'SceneLayers', 'QTabWidget', 'QCommandLinkButton', 'QGraphicsSceneContextMenuEvent', 'QScrollArea', 'QTableView', 'QCommonStyle', 'QGraphicsSceneDragDropEvent', 'QScrollBar', 'QTableWidget', 'QCompleter', 'QGraphicsSceneEvent', 'QScroller', 'QTableWidgetItem', 'ControlTypes', 'QGraphicsSceneHelpEvent', 'QScrollerProperties', 'QTableWidgetSelectionRange', 'CornerWidgets', 'QGraphicsSceneHoverEvent', 'Sections', 'TakeRowResult', 'QDataWidgetMapper', 'QGraphicsSceneMouseEvent', 'QShortcut', 'QTapAndHoldGesture', 'QDateEdit', 'QGraphicsSceneMoveEvent', 'QSizeGrip', 'QTapGesture', 'QDateTimeEdit', 'QGraphicsSceneResizeEvent', 'QSizePolicy', 'QTextBrowser', 'QDesktopWidget', 'QGraphicsSceneWheelEvent', 'QSlider', 'QTextEdit', 'QDial', 'QGraphicsSimpleTextItem', 'QSpacerItem', 'QTimeEdit', 'QDialog', 'QGraphicsTextItem', 'QSpinBox', 'QToolBar', 'QDialogButtonBox', 'QGraphicsTransform', 'QSplashScreen', 'ToolBarFeatures', 'QDirModel', 'QGraphicsView', 'QSplitter', 'QToolBox', 'DockOptions', 'QGraphicsWidget', 'QSplitterHandle', 'QToolButton', 'QDockWidget', 'QGridLayout', 'QStackedLayout', 'ToolButtonFeatures', 'DockWidgetFeatures', 'QGroupBox', 'QStackedWidget', 'QToolTip', 'QDoubleSpinBox', 'QHBoxLayout', 'StandardButtons', 'QTreeView', 'EditTriggers', 'QHeaderView', 'StandardButtons', 'QTreeWidget', 'QErrorMessage', 'QInputDialog', 'State', 'QTreeWidgetItem', 'ExtraSelection', 'InputDialogOptions', 'QStatusBar', 'QTreeWidgetItemIterator', 'QFileDialog', 'QItemDelegate', 'StepEnabled', 'QUndoCommand', 'QFileIconProvider', 'QItemEditorCreatorBase', 'QStyle', 'QUndoGroup', 'QFileSystemModel', 'QItemEditorFactory', 'QStyleFactory', 'QUndoStack', 'QFocusFrame', 'IteratorFlags', 'QStyleHintReturn', 'QUndoView', 'QFontComboBox', 'QKeyEventTransition', 'QStyleHintReturnMask', 'QVBoxLayout', 'QFontDialog', 'QKeySequenceEdit', 'QStyleHintReturnVariant', 'ViewItemFeatures', 'FontDialogOptions', 'QLCDNumber', 'QStyleOption', 'QWhatsThis', 'FontFilters', 'QLabel', 'QStyleOptionButton', 'QWidget', 'QFormLayout', 'QLayout', 'QStyleOptionComboBox', 'QWidgetAction', 'QFrame', 'QLayoutItem', 'QStyleOptionComplex', 'QWidgetItem', 'FrameFeatures', 'QLineEdit', 'QStyleOptionDockWidget', 'QWizard', 'QGesture', 'QListView', 'QStyleOptionFocusRect', 'WizardOptions', 'QGestureEvent', 'QListWidget', 'QStyleOptionFrame', 'QWizardPage', 'QGestureRecognizer', 'QListWidgetItem', 'QStyleOptionGraphicsItem']


libs = [PYQT5, PYQT4, PYSIDE]
for lib in libs:
    try:
        __import__(lib)
        QT_ENV = lib
        break
    except ImportError:
        pass

if QT_ENV is None:
    raise Exception("No Qt Enviroment was detected!")

if QT_ENV == PYQT5:
    from PyQt5 import QtGui, QtCore, QtWidgets
else:
    if QT_ENV == PYQT4:
        from PyQt4 import QtGui, QtCore

    elif QT_ENV == PYSIDE:
        from PySide import QtGui, QtCore
        import PySide
        QtCore.QT_VERSION_STR = PySide.QtCore.__version__
        QtCore.PYQT_VERSION_STR = PySide.__version__
    QtWidgets = QtGui
    QtCore.QSortFilterProxyModel = QtGui.QSortFilterProxyModel
    QtWidgets.QStyleOptionProgressBar = QtGui.QStyleOptionProgressBarV2

    class NewQHeaderView(QtWidgets.QHeaderView):
        def setSectionsMovable(self, *args, **kwargs):
            self.setMovable(*args, **kwargs)

        def setSectionsClickable(self, *args, **kwargs):
            self.setClickable(*args, **kwargs)

        def setSectionResizeMode(self, *args, **kwargs):
            self.setResizeMode(*args, **kwargs)

    QtWidgets.QHeaderView = NewQHeaderView

    class NewQFileDialog(QtWidgets.QFileDialog):
        def getOpenFileName(self, *args, **kwargs):
            self.getOpenFileNamesAndFilter(*args, **kwargs)

    QtWidgets.QFileDialog = NewQFileDialog
