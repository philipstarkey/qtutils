import sys

from PySide.QtCore import *
from PySide.QtGui import *
from qtutils.widgets.analogoutput import AnalogOutput
from qtutils.widgets.digitaloutput import DigitalOutput

class DDSOutput(QWidget):
    def __init__(self, hardware_name, connection_name='-', parent=None):
        QWidget.__init__(self,parent)
        
        self._connection_name = connection_name
        self._hardware_name = hardware_name
        
        label_text = (self._hardware_name + ' - ' + self._connection_name) 
        self._label = QLabel(label_text)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Minimum)
        
        
        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Minimum)
        
        # Create widgets
        self._widgets = {}
        self._widgets['gate'] = DigitalOutput('Enabled')
        self._widgets['freq'] = AnalogOutput('',display_name='Frequency', horizontal_alignment=True)
        self._widgets['amp'] = AnalogOutput('',display_name='Amplitude', horizontal_alignment=True)
        self._widgets['phase'] = AnalogOutput('',display_name='Phase', horizontal_alignment=True)
        
        # Create grid layout that keeps widgets from expanding and keeps label centred above the widgets
        self._layout = QGridLayout(self)
        self._layout.setVerticalSpacing(0)
        self._layout.setHorizontalSpacing(0)
        self._layout.setContentsMargins(0,0,0,0)
        
        h_widget = QWidget()            
        h_layout = QHBoxLayout(h_widget)
        h_layout.setContentsMargins(0,0,0,0)
        h_layout.addWidget(self._widgets['gate'])
        h_layout.addWidget(self._widgets['freq'])
        h_layout.addWidget(self._widgets['amp'])
        h_layout.addWidget(self._widgets['phase'])
        
        self._layout.addWidget(self._label,0,0)
        #self._layout.addItem(QSpacerItem(0,0,QSizePolicy.MinimumExpanding,QSizePolicy.Minimum),0,1)
        self._layout.addWidget(h_widget,1,0)            
        #self._layout.addItem(QSpacerItem(0,0,QSizePolicy.MinimumExpanding,QSizePolicy.Minimum),1,1)
        self._layout.addItem(QSpacerItem(0,0,QSizePolicy.Minimum,QSizePolicy.MinimumExpanding),2,0)
        
        
    def get_sub_widget(self,subchnl):
        if subchnl in self._widgets:
            return self._widgets[subchnl]
        
        raise RuntimeError('The sub-channel %s must be either gate, freq, amp or phase'%subchnl)
        
    def hide_sub_widget(self,subchnl):
        if subchnl in self._widgets:
            self._widgets[subchnl].hide()
            return
        
        raise RuntimeError('The sub-channel %s must be either gate, freq, amp or phase'%subchnl)  
    
    def show_sub_widget(self,subchnl):
        if subchnl in self._widgets:
            self._widgets[subchnl].show()
            return
        
        raise RuntimeError('The sub-channel %s must be either gate, freq, amp or phase'%subchnl)
        
# A simple test!
if __name__ == '__main__':
    
    qapplication = QApplication(sys.argv)
    
    window = QWidget()
    layout = QVBoxLayout(window)
    button = DDSOutput('DDS1')
        
    layout.addWidget(button)
    
    window.show()
    
    
    sys.exit(qapplication.exec_())
    