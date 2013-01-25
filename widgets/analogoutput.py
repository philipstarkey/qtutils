import sys

from PySide.QtCore import *
from PySide.QtGui import *

from IPython import embed

class AnalogOutput(QWidget):
    def __init__(self, hardware_name, connection_name='-', display_name=None, horizontal_alignment=False, parent=None):
        QWidget.__init__(self,parent)
        
        self._connection_name = connection_name
        self._hardware_name = hardware_name
        
        label_text = (self._hardware_name + '\n' + self._connection_name) if display_name is None else display_name
        self._label = QLabel(label_text)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self._spin_widget = QDoubleSpinBox()
        self._spin_widget.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self._combobox = QComboBox()
        self._combobox.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        
        # Handle spinbox context menu
        self._lock_action = QAction("Lock",self._spin_widget)
        self._lock_action.triggered.connect(lambda:self._menu_triggered(self._lock_action))
        
        self._stepup_action = QAction("Step up",self._spin_widget)
        self._stepup_action.triggered.connect(lambda:self._spin_widget.stepBy(1))
        self._stepdown_action = QAction("Step down",self._spin_widget)
        self._stepdown_action.triggered.connect(lambda:self._spin_widget.stepBy(-1))
            
        def context_menu(pos):
            menu = self._spin_widget.lineEdit().createStandardContextMenu()
            # Add Divider
            menu.addSeparator()
            # Add step up/Stepdown actions (grey out if at min/max or locked)
            menu.addAction(self._stepup_action)
            menu.addAction(self._stepdown_action)
            if self._spin_widget.value() == self._spin_widget.minimum():
                self._stepdown_action.setEnabled(False)
            else:
                self._stepdown_action.setEnabled(True)
            if self._spin_widget.value() == self._spin_widget.maximum():
                self._stepup_action.setEnabled(False)
            else:
                self._stepup_action.setEnabled(True)
            
            # Add divider
            menu.addSeparator()
            # Add lock action
            menu.addAction(self._lock_action)
            
            # Show the menu
            menu.popup(self.mapToGlobal(pos))
            
        self._spin_widget.lineEdit().setContextMenuPolicy(Qt.CustomContextMenu)
        self._spin_widget.lineEdit().customContextMenuRequested.connect(context_menu)
        
        # Create widgets and layouts        
        if horizontal_alignment:
            self._layout = QHBoxLayout(self)
            #self._layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
            self._layout.addWidget(self._label)
            self._layout.addWidget(self._spin_widget)
            self._layout.addWidget(self._combobox)
        else:
            self._layout = QGridLayout(self)
            self._layout.setVerticalSpacing(0)
            self._layout.setHorizontalSpacing(0)
            self._layout.setContentsMargins(0,0,0,0)
            
            self._layout.addWidget(self._label)            
            self._layout.addItem(QSpacerItem(0,0,QSizePolicy.MinimumExpanding,QSizePolicy.Minimum),0,1)
            
            h_widget = QWidget()            
            h_layout = QHBoxLayout(h_widget)
            h_layout.setContentsMargins(0,0,0,0)
            h_layout.addWidget(self._spin_widget)
            h_layout.addWidget(self._combobox)
            
            self._layout.addWidget(self._label,0,0)
            self._layout.addWidget(h_widget,1,0)            
            self._layout.addItem(QSpacerItem(0,0,QSizePolicy.MinimumExpanding,QSizePolicy.Minimum),1,1)
            self._layout.addItem(QSpacerItem(0,0,QSizePolicy.Minimum,QSizePolicy.MinimumExpanding),2,0)
        
        # Install the event filter that will allow us to catch right click mouse release events so we can popup a menu even when the button is disabled
        self.installEventFilter(self)
        
        #self._spin_widget.lineEdit().addAction(self._action)
        #self._spin_widget.lineEdit().setContextMenuPolicy(Qt.ActionsContextMenu);
        
        # The Analog Out object that is in charge of this button
        self._AO = None
    
    # Setting and getting methods for the Digitl Out object in charge of this button
    def set_AO(self,AO):
        # If we are setting a new AO, remove this widget from the old one (if it isn't None) and add it to the new one (if it isn't None)
        if AO != self._AO:
            if self._AO is not None:
                self._AO.remove_widget(self)
            if AO is not None:
                AO.add_widget(self)
        # Store a reference to the digital out object
        self._AO = AO
        
    def get_AO(self):
        return self._AO
    
    # The event filter that pops up a context menu on a right click, even when the button is disabled
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.RightButton:
            menu = QMenu(self)
            menu.addAction("Lock" if self._spin_widget.isEnabled() else "Unlock")
            menu.triggered.connect(self._menu_triggered)
            menu.popup(self.mapToGlobal(event.pos()))
        
        return QPushButton.eventFilter(self, obj, event)
     
    # This method is called whenever an entry in the context menu is clicked
    def _menu_triggered(self,action):
        if action.text() == "Lock":
            self.lock()
        elif action.text() == "Unlock":
            self.unlock()
    
    # This method locks (disables) the widget, and if the widget has a parent AO object, notifies it of the lock
    def lock(self):        
        self._spin_widget.setEnabled(False)
        self._lock_action.setText("Unlock")
        if self._AO is not None:
            self._AO.lock()
    
    # This method unlocks (enables) the widget, and if the widget has a parent AO object, notifies it of the unlock    
    def unlock(self):        
        self._spin_widget.setEnabled(True)        
        self._lock_action.setText("Lock")
        if self._AO is not None:
            self._AO.unlock()
        
    
# A simple test!
if __name__ == '__main__':
    
    qapplication = QApplication(sys.argv)
    
    window = QWidget()
    layout = QVBoxLayout(window)
    button = AnalogOutput('AO1')
        
    layout.addWidget(button)
    
    window.show()
    
    
    sys.exit(qapplication.exec_())
    