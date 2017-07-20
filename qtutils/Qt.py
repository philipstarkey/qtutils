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
elif QT_ENV == PYQT4:
    import sip

    # Have to set PyQt API via sip before importing PyQt:
    API_NAMES = ["QDate", "QDateTime", "QString", "QTextStream", "QTime", "QUrl", "QVariant"]
    API_VERSION = 2
    for name in API_NAMES:
        sip.setapi(name, API_VERSION)

    from PyQt4 import QtGui, QtCore
    QtWidget = QtGui
elif QT_ENV == PYSIDE:
    from PySide import QtGui, QtCore
    QtWidget = QtGui