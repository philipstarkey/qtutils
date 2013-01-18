import sys

from PySide.QtCore import *
from PySide.QtGui import *

from IPython import embed

class ToolPalette(QScrollArea):
    def __init__(self,*args,**kwargs):
        QScrollArea.__init__(self,*args,**kwargs)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum)
        # create the grid layout
        #self.setWidget(QWidget(self))
        #self.widget().setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        self._layout = QGridLayout(self) 
        #self._layout.setMaximumSize(QSize(524287,524287))
        #self._layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self._widget_list = []
        
        # need to keep track of these internally because the GridLayout returns the number of 
        # allocated rows/columns with columnCount()/RowCount() rather than the number of visible ones
        self._column_count = 0
        self._row_count = 0
        
    
    def addWidget(self,widget):
        # Append to end of tool pallete
        widget.clicked.connect(embed)
        self._widget_list.append(widget)
        self._layout_widgets()
        
    def insertWidget(self,index,widget):
        # Insert into position 'index'
        self._widget_list.insert(index,widget)
        self._layout_widgets()
        
    def _layout_widgets(self):
        # find the minimum size of the widest widget in the grid layout
        w_size_hints = [w.minimumSizeHint().width() for w in self._widget_list]
        h_size_hints = [w.sizeHint().height() for w in self._widget_list]
        max_width = max(w_size_hints)
       
        
        # find the width of the gridlayout
        layout_width = self.size().width()
        #layout_width = self._layout.sizeHint().width()
        layout_spacing = self._layout.horizontalSpacing()
        
        
        
        # How many widgets can fit in a row?
        # TODO: remove layoutspacing*columncount
        num_widgets_per_row = int((layout_width+layout_spacing*self._column_count)/max_width)
        
        
        if num_widgets_per_row < 1:
            num_widgets_per_row = 1
        elif num_widgets_per_row > len(self._widget_list):
            num_widgets_per_row = len(self._widget_list)
            
        if num_widgets_per_row != self._column_count:            
            print 'changing number of columns'
            # remove all widgets
            for widget in self._widget_list:
                self._layout.removeWidget(widget)
            
            # re add all widgets into the grid layout
            row = 0
            column = 0
            for widget in self._widget_list:
                self._layout.addWidget(widget,row,column)
                column += 1
                if column >= num_widgets_per_row:
                    column = 0
                    row += 1
                    
            # update the row/column count
            
            # This is here because the row count may have been increased at the end of the insertion
            # loop
            if column != 0:
                row += 1
            self._column_count = num_widgets_per_row
            self._row_count = row

            print (max(h_size_hints)+self._layout.verticalSpacing())*self._row_count+self._layout.verticalSpacing()*2
            print max(h_size_hints)
            print self._layout.verticalSpacing()
            print self._row_count
            
            self.setMinimumSize(QSize(self.minimumSize().width(),(max(h_size_hints)+self._layout.verticalSpacing())*self._row_count+self._layout.verticalSpacing()*2))
            for i in range(self._layout.rowCount()):
                if i < self._row_count:
                    self._layout.setRowMinimumHeight(i,max(h_size_hints))
                else:
                    self._layout.setRowMinimumHeight(i,0)
        # re apply focus?

    def resizeEvent(self, event):
        # overwrite the resize event!
        print '---------'
        print self._widget_list[0].size()
        print self._widget_list[0].sizeHint()
        print self._widget_list[0].minimumSizeHint()
        print self._layout.rowMinimumHeight(0)
        print self.size()
        print self.minimumSize()
        print self.sizeHint()
        print self.minimumSizeHint()
        # pass resize event on to qwidget
        # call layout()
        QWidget.resizeEvent(self,event)
        self._layout_widgets()



if __name__ == '__main__':
    
    qapplication = QApplication([])
    
    window = QWidget()
    layout = QVBoxLayout(window)
    toolpalette = ToolPalette()
    layout.addWidget(toolpalette)
    layout.addItem(QSpacerItem(0,0,QSizePolicy.Minimum,QSizePolicy.MinimumExpanding))
    for i in range(20):
        button = QPushButton('Button %d'%i)
        
        button.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        toolpalette.addWidget(button)
    window.show()
    
    
    sys.exit(qapplication.exec_())
    