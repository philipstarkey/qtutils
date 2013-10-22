import sys

from PySide.QtCore import *
from PySide.QtGui import *


class DigitalOutput(QPushButton):
    def __init__(self,*args,**kwargs):
        QPushButton.__init__(self,*args,**kwargs)
        
        # Install the event filter that will allow us to catch right click mouse release events so we can popup a menu even when the button is disabled
        self.installEventFilter(self)
        self.setCheckable(True)
        
        # The Digital Out object that is in charge of this button
        self._DO = None
    
    # Setting and getting methods for the Digitl Out object in charge of this button
    def set_DO(self,DO,notify_old_DO=True,notify_new_DO=True):
        # If we are setting a new DO, remove this widget from the old one (if it isn't None) and add it to the new one (if it isn't None)
        if DO != self._DO:
            if self._DO is not None and notify_old_DO:
                self._DO.remove_widget(self)
            if DO is not None and notify_new_DO:
                DO.add_widget(self)
        # Store a reference to the digital out object
        self._DO = DO
        
    def get_DO(self):
        return self._DO
    
    # The event filter that pops up a context menu on a right click, even when the button is disabled
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.RightButton:
            menu = QMenu(self)
            menu.addAction("Lock" if self.isEnabled() else "Unlock")
            menu.triggered.connect(self._menu_triggered)
            menu.popup(self.mapToGlobal(event.pos()))
        
        return QPushButton.eventFilter(self, obj, event)
     
    # This method is called whenever an entry in the context menu is clicked
    def _menu_triggered(self,action):
        if action.text() == "Lock":
            self.lock()
        elif action.text() == "Unlock":
            self.unlock()
    
    # This method locks (disables) the widget, and if the widget has a parent DO object, notifies it of the lock
    def lock(self,notify_do=True):        
        self.setEnabled(False)
        if self._DO is not None and notify_do:
            self._DO.lock()
    
    # This method unlocks (enables) the widget, and if the widget has a parent DO object, notifies it of the unlock    
    def unlock(self,notify_do=True): 
        self.setEnabled(True)
        if self._DO is not None and notify_do:
            self._DO.unlock()
        
    @property
    def state(self):
        return self.isChecked()
        
    @state.setter
    def state(self,state):
        # conversion to integer, then bool means we can safely pass in
        # either a string '1' or '0', True or False or 1 or 0
        self.setChecked(bool(int(state)))
    
# A simple test!
if __name__ == '__main__':
    
    qapplication = QApplication(sys.argv)
    
    window = QWidget()
    layout = QVBoxLayout(window)
    button = DigitalOutput('very very long Button')
        
    layout.addWidget(button)
    
    window.show()
    
    
    sys.exit(qapplication.exec_())
    