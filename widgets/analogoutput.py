import sys

from PySide.QtCore import *
from PySide.QtGui import *

class AnalogOutput(QWidget):
    def __init__(self, hardware_name, connection_name='-', display_name=None, horizontal_alignment=False, parent=None):
        QWidget.__init__(self,parent)
        
        self._connection_name = connection_name
        self._hardware_name = hardware_name
        
        label_text = (self._hardware_name + '\n' + self._connection_name) if display_name is None else display_name
        self._label = QLabel(label_text)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Minimum)
        self._spin_widget = QDoubleSpinBox()
        self._spin_widget.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Minimum)
        self._spin_widget.setKeyboardTracking(False)
        self._combobox = QComboBox()
        self._combobox.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self._combobox.currentIndexChanged.connect(self._on_combobox_change)
        
        self._value_changed_function = None
        
        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Minimum)
        
        # Handle spinbox context menu
        # Lock/Unlock action
        self._lock_action = QAction("Lock",self._spin_widget)
        self._lock_action.triggered.connect(lambda:self._menu_triggered(self._lock_action))
        #change step size action
        self._stepsize_action = QAction("Set step size",self._spin_widget)
        self._stepsize_action.triggered.connect(self._change_step)
        # Stepup/down Actions
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
            menu.addAction(self._stepsize_action)
            
            # Show the menu
            menu.popup(self.mapToGlobal(pos))
            
        self._spin_widget.lineEdit().setContextMenuPolicy(Qt.CustomContextMenu)
        self._spin_widget.lineEdit().customContextMenuRequested.connect(context_menu)
        
        # Create widgets and layouts        
        if horizontal_alignment:
            self._layout = QHBoxLayout(self)
            self._layout.addWidget(self._label)
            self._layout.addWidget(self._spin_widget)
            self._layout.addWidget(self._combobox)
        else:
            self._layout = QGridLayout(self)
            self._layout.setVerticalSpacing(0)
            self._layout.setHorizontalSpacing(0)
            self._layout.setContentsMargins(5,5,5,5)
            
            self._label.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Minimum)
            
            #self._layout.addWidget(self._label)            
            #self._layout.addItem(QSpacerItem(0,0,QSizePolicy.MinimumExpanding,QSizePolicy.Minimum),0,1)
            
            h_widget = QWidget()            
            h_layout = QHBoxLayout(h_widget)
            h_layout.setContentsMargins(0,0,0,0)
            h_layout.addWidget(self._spin_widget)
            h_layout.addWidget(self._combobox)
            
            self._layout.addWidget(self._label,0,0)
            self._layout.addWidget(h_widget,1,0)            
            #self._layout.addItem(QSpacerItem(0,0,QSizePolicy.MinimumExpanding,QSizePolicy.Minimum),1,1)
            self._layout.addItem(QSpacerItem(0,0,QSizePolicy.Minimum,QSizePolicy.MinimumExpanding),2,0)
        
        # Install the event filter that will allow us to catch right click mouse release events so we can popup a menu even when the button is disabled
        self.installEventFilter(self)
        
        # The Analog Out object that is in charge of this button
        self._AO = None
    
    # Setting and getting methods for the Digitl Out object in charge of this button
    def set_AO(self,AO,notify_old_AO=True,notify_new_AO=True):
        # If we are setting a new AO, remove this widget from the old one (if it isn't None) and add it to the new one (if it isn't None)
        if AO != self._AO:
            if self._AO is not None and notify_old_AO:
                self._AO.remove_widget(self,False)
            if AO is not None and notify_new_AO:
                AO.add_widget(self)
        # Store a reference to the digital out object
        self._AO = AO
        
    def get_AO(self):
        return self._AO
    
    def connect_value_change(self,func):
        self._value_changed_function = lambda value,self=self: func(value,self.selected_unit,True)
        self._spin_widget.valueChanged.connect(self._value_changed_function)
        
    def disconnect_value_change(self):
        self._spin_widget.valueChanged.disconnect(self._value_changed_function)
    
    def set_combobox_model(self,model):
        self._combobox.setModel(model)
    
    def _on_combobox_change(self):
        selected_text = self.selected_unit
        if self._AO is not None:
            self._AO.change_unit(selected_text)
            
    def block_spinbox_signals(self):
        return self._spin_widget.blockSignals(True)
        
    def unblock_spinbox_signals(self):
        return self._spin_widget.blockSignals(False)
    
    def set_spinbox_value(self,value,unit):
        if self._AO is not None:
            # get the value in the selected unit
            value = self._AO.convert_value_to_base(value,unit)
            value = self._AO.convert_value_from_base(value,self.selected_unit)            
        self._spin_widget.setValue(value)
    
    @property
    def selected_unit(self):
        return self._combobox.currentText()
    
    def block_combobox_signals(self):
        return self._combobox.blockSignals(True)
        
    def unblock_combobox_signals(self):
        return self._combobox.blockSignals(False)
    
    def set_selected_unit(self,unit):
        if unit != self.selected_unit:
            item = self._combobox.model().findItems(unit)
            if item:
                model_index = self._combobox.model().indexFromItem(item[0])
                self._combobox.setCurrentIndex(model_index.row())
                
    def set_num_decimals(self,decimals):
        self._spin_widget.setDecimals(decimals)
        
    def set_limits(self,lower,upper):
        self._spin_widget.setRange(lower,upper)
        
    def set_step_size(self,step):
        self._spin_widget.setSingleStep(step)
            
    def _change_step(self):
        maximum_step = abs(self._spin_widget.maximum()-self._spin_widget.minimum())
        new_step,ok = QInputDialog.getDouble(self,"Set step size","Set step size",self._spin_widget.singleStep(),0.0,maximum_step,self._spin_widget.decimals())
    
        if ok:
            self.set_step_size(new_step)
            if self._AO:
                self._AO.set_step_size(new_step,self.selected_unit)
    
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
    def lock(self,notify_ao=True):        
        self._spin_widget.setEnabled(False)
        self._lock_action.setText("Unlock")
        if self._AO is not None and notify_ao:
            self._AO.lock()
    
    # This method unlocks (enables) the widget, and if the widget has a parent AO object, notifies it of the unlock    
    def unlock(self,notify_ao=True):        
        self._spin_widget.setEnabled(True)        
        self._lock_action.setText("Lock")
        if self._AO is not None and notify_ao:
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
    