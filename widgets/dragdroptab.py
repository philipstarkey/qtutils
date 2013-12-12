import sys
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import QUiLoader

from qtutils import *

debug = False
def print_debug(s):
    if debug:
        print s

class DragDropTabBar(QTabBar):
    def __init__(self, tab_widget):
        QTabBar.__init__(self)
        self.setAcceptDrops(True)              
        self.previous_active_tab = None   
        self.tab_widget = tab_widget
        
        # This code could be in the DragDropTabWidget class...
        self.tab_widget.setTabBar(self)
        self.tab_widget.setMovable(True)    

        self.enable_reorder_while_dragging = True
        self.havent_left_source_tab = False        
    
    def get_tab_information(self,index):
        tab_data = self.tab_widget.tabBar().tabData(index)
        text_colour = self.tab_widget.tabBar().tabTextColor(index)
        tooltip = self.tab_widget.tabBar().tabToolTip(index)
        whats_this = self.tab_widget.tabBar().tabWhatsThis(index)
        button_left = self.tab_widget.tabBar().tabButton(index,QTabBar.LeftSide)
        button_right = self.tab_widget.tabBar().tabButton(index,QTabBar.RightSide)
        icon = self.tab_widget.tabBar().tabIcon(index)
        
        return tab_data,text_colour,tooltip,whats_this,button_left,button_right,icon
        
    def set_tab_information(self,index,data):
        tab_data,text_colour,tooltip,whats_this,button_left,button_right,icon = data
        if tab_data:
            self.tab_widget.tabBar().setTabData(index,tab_data)
        self.tab_widget.tabBar().setTabTextColor(index,text_colour)
        if tooltip:
            self.tab_widget.tabBar().setTabToolTip(index,tooltip)
        if whats_this:
            self.tab_widget.tabBar().setTabWhatsThis(index,whats_this)
        if button_left:
            self.tab_widget.tabBar().setTabButton(index,QTabBar.LeftSide,button_left)
        if button_right:
            self.tab_widget.tabBar().setTabButton(index,QTabBar.RightSide,button_right)
        if icon:
            self.tab_widget.tabBar().setTabIcon(index,icon)
            
    def mouseMoveEvent(self, e):
        # forward the event on...
        QTabBar.mouseMoveEvent(self, e)        
        e.accept()
        
        # Get the group this tab belongs to...
        tabgroup = self.tab_widget.get_tab_widget_group()
                
        # if we are still dragging within the tabbar, or we are in group -1, then don't
        # do anything special, and just pass the event along
        if tabgroup.id == -1 or (self.x() < e.x() < (self.x() + self.width()) and 
            self.y() < e.y() < (self.y() + self.height())):
            pass
            
        # Else if we are not in a movement already and we are dragging with the left mouse button
        # outside of the tab bar, then begin the drag!
        elif tabgroup.moving_tab_data == None and e.buttons()&Qt.LeftButton:
            # Save all information pertaining to the tab
            current_index = self.currentIndex()
            text = self.tab_widget.tabText(current_index)
            #icon = self.tab_widget.tabIcon(current_index)
            tab_properties = self.get_tab_information(current_index)
            #widget = self.tab_widget.currentWidget()
            widget = self.tab_widget.widget(current_index)
            tabgroup.moving_tab_data = self.find_notebook_index(), current_index, text, tab_properties, widget
            
            self.havent_left_source_tab = True
            
            # A hack to force position of tab if we switch from a reorder state to a drag state
            finishMoveEvent = QMouseEvent(QEvent.MouseMove, e.pos(), Qt.NoButton, Qt.NoButton, Qt.NoModifier);
            self.mouseMoveEvent(finishMoveEvent);
            #QCoreApplication.postEvent(self,finishMoveEvent)
            
            # Start the drag
            drag = QDrag(self)
            mimeData = QMimeData()
            mimeData.setData("DragDropTabBar",QByteArray(str(tabgroup.id)))
            drag.setMimeData(mimeData)
            # This pauses the main loop and only runs the overridden drag/drop functions in this class below
            dropAction = drag.exec_(Qt.MoveAction)
            
            # If we didn't drop on an accepting target, reset the storage and make sure the tab isn't in no mans land!
            #if dropAction == Qt.IgnoreAction:
            if tabgroup.moving_tab_data and tabgroup.moving_tab_data[0] == -1:
            # The tab is in no mans land...let's put it back somewhere nice
                self.tab_widget.insertTab(current_index, widget, text)
                self.set_tab_information(current_index, tab_properties)
                self.tab_widget.setCurrentIndex(current_index)
                tabgroup.moving_tab_data = self.find_notebook_index(), current_index, text, tab_properties, widget
                    
            # Force all animations to finish properly in all tab bars application wide
            self.finish_animation()
            
            # Make sure the moved page is focussed
            # Get the data again, so that it is current
            notebook_index, index, text, tab_properties, widget = tabgroup.moving_tab_data
            self.fix_displayed_tab(notebook_index,index,widget)
            
            # reset variables
            tabgroup.moving_tab_data = None
            self.previous_active_tab = None
            self.havent_left_source_tab = False
    
    def dragMoveEvent(self, e):
        # get the tabgroup
        tabgroup = self.tab_widget.get_tab_widget_group()
        
        # if we don't have id==-1 (we support dragging to and from this notebook)
        # If the mimetype matches, and the id in the mimetype matches, we can accept the drag/drop event
        mime_data_id = -1
        try:
            mime_data_id = int(e.mimeData().data("DragDropTabBar"))
        except Exception:
            pass
        if self.enable_reorder_while_dragging and mime_data_id == tabgroup.id and tabgroup.id != -1 and tabgroup.moving_tab_data:
            notebook_index, index, text, tab_properties, widget = tabgroup.moving_tab_data
            
            print_debug('move event for notebook %d in group %d'%(self.find_notebook_index(),tabgroup.id))
            
            # Find the x position of the mouse
            x_pos = e.pos().x()
            # find which tab is located at that position
            tab_at_mouse = self.tabAt(QPoint(x_pos,self.y()))
            
            # If we go 2 px either side of this position, do we always get the same tab?
            # if we do, then we can proceed, otherwise hold off until we are further away from the boundary between two tabs, as this renders much nicer!
            tab_at_mouse_l = self.tabAt(QPoint(x_pos-2,self.y()))
            tab_at_mouse_r = self.tabAt(QPoint(x_pos+2,self.y()))
            if tab_at_mouse_l != tab_at_mouse_r:
                tab_at_mouse = index
            
            if tab_at_mouse == -1:
                if x_pos < self.x():
                    tab_at_mouse = 0
                else:
                    tab_at_mouse = self.tab_widget.count()-1
            
            # move our tab to that location (ignore if already at the location
            if tab_at_mouse != index and index != -1:
                e.accept()
                print_debug('Moving tab index: %d, Index at mouse: %d'%(index,tab_at_mouse))
                # Update the location of the previous active tab?
                # If the moving tab is before the previous active tab, the previous active tab will be moving down by 1
                if self.previous_active_tab:
                    print_debug(self.previous_active_tab)
                    if index < self.previous_active_tab:
                        self.previous_active_tab -= 1
                    # If the moving tab is going to a position before the previous active tab, then the previous active tab will be 
                    # moving up by 1
                    if tab_at_mouse < self.previous_active_tab:
                        self.previous_active_tab += 1
                
                # Move our tab to the new position
                self.moveTab(index,tab_at_mouse)
                self.tab_widget.setCurrentIndex(0) # we have to force the tabWidget to update the page...
                self.tab_widget.setCurrentIndex(1) # we have to force the tabWidget to update the page...
                self.tab_widget.setCurrentIndex(tab_at_mouse) # we have to force the tabWidget to update the page...
                self.tab_widget.setCurrentWidget(widget) # we have to force the tabWidget to update the page...
                
                print_debug(self.tab_widget.currentWidget())
                print_debug(widget)
                
                print_debug('widget count afer move: %d'%(self.tab_widget.count()))
                
                # Update the moving tab data to the new position
                tabgroup.moving_tab_data = notebook_index, tab_at_mouse, text, self.get_tab_information(tab_at_mouse), widget
                print_debug(tabgroup.moving_tab_data)
        
        QTabBar.dragMoveEvent(self,e)
    
    # We are leaving the notebook...
    def dragLeaveEvent(self, e):
        # get the tabgroup
        tabgroup = self.tab_widget.get_tab_widget_group()
        
        print_debug('leave event for notebook %d in group %d'%(self.find_notebook_index(),tabgroup.id))
                
        # if we don't have id==-1 (we support dragging to and from this notebook)
        if tabgroup.id != -1 and tabgroup.moving_tab_data:
            e.accept()
            # We restore the active tab now, incase the indexs change when removing our moving tab
            # Only restore the previous active tab if we stored it on a dragEnterEvent
            # This will preserve the selectionBehaviorOnRemove property for the source notebook
            if self.previous_active_tab:
                print_debug('Previous_active_tab: %d'%(self.previous_active_tab))
                self.tab_widget.setCurrentIndex(self.previous_active_tab)
                self.previous_active_tab = None
        
            # Remove the tab from the notebook we are leaving
            notebook_index, index, text, tab_properties, widget = tabgroup.moving_tab_data
            tab_properties = self.get_tab_information(index)
            self.tab_widget.removeTab(index)
            tabgroup.moving_tab_data = -1, -1, text, tab_properties, widget
            print_debug('Moving tab index: %d'%index)
            print_debug('widget count (after remove): %d'%(self.tab_widget.count()))
            print_debug(tabgroup.moving_tab_data)
                
        QTabBar.dragLeaveEvent(self, e)
            
    def dragEnterEvent(self, e):
        # get the tabgroup
        tabgroup = self.tab_widget.get_tab_widget_group()
        
        print_debug('enter event for notebook %d in group %d'%(self.find_notebook_index(),tabgroup.id))
        
        # if we don't have id==-1 (we support dragging to and from this notebook)
        # If the mimetype matches, and the id in the mimetype matches, we can accept the drag/drop event
        mime_data_id = -1
        try:
            mime_data_id = int(e.mimeData().data("DragDropTabBar"))
        except Exception:
            pass
        if mime_data_id == tabgroup.id and tabgroup.id != -1 and tabgroup.moving_tab_data:
            print_debug('Accepting event')
            e.accept()
            notebook_index, index, text, tab_properties, widget = tabgroup.moving_tab_data
            # Save the current active tab incase we don't drop here
            if self.havent_left_source_tab is not True:
                print_debug('setting previous_active_tab')
                self.previous_active_tab = self.tab_widget.currentIndex()
            
            # Add the tab to this notebook
            self.tab_widget.addTab(widget, text)
            current_index = self.tab_widget.count()-1
            self.tab_widget.setCurrentIndex(current_index)
            self.set_tab_information(current_index,tab_properties)
            print_debug('widget count (after add): %d'%(self.tab_widget.count()))
            # Update the moving tab data
            tabgroup.moving_tab_data = self.find_notebook_index(), self.tab_widget.count()-1, text, tab_properties, widget
            print_debug(tabgroup.moving_tab_data)
        
        # if self.havent_left_source_tab:
            # self.havent_left_source_tab = False
        QTabBar.dragEnterEvent(self, e)
        
    def dropEvent(self, e):
        # get the tabgroup
        tabgroup = self.tab_widget.get_tab_widget_group()
        
        print_debug('drop event for notebook %d in group %d'%(self.find_notebook_index(),tabgroup.id))
        
        # if we don't have id==-1 (we support dragging to and from this notebook)
        # If the mimetype matches, and the id in the mimetype matches, we can accept the drag/drop event
        mime_data_id = -1
        try:
            mime_data_id = int(e.mimeData().data("DragDropTabBar"))
        except Exception:
            pass
        if mime_data_id == tabgroup.id and tabgroup.id != -1 and tabgroup.moving_tab_data:
            e.accept()
        QTabBar.dropEvent(self, e)
        
    # Hack to show the correct widget after dropping (bug introduced when allowing reordering to occur while dragging)
    @inmain_decorator(wait_for_return=False)  
    def fix_displayed_tab(self,notebook_index,index,widget):
        tabgroup = self.tab_widget.get_tab_widget_group()
        # change the current index to two different points, so that we are guaranteed to avoid Qt ignoring our request to reselect the
        # correct widget
        QTabBar.setCurrentIndex(tabgroup.widget_list[notebook_index].tab_bar,0)
        QTabBar.setCurrentIndex(tabgroup.widget_list[notebook_index].tab_bar,1)
        tabgroup.widget_list[notebook_index].setCurrentWidget(widget)
        
    # Hack to make any misplaced tab widgets animate back to their correct position
    @inmain_decorator(wait_for_return=False)  
    def finish_animation(self):
        tabgroup = self.tab_widget.get_tab_widget_group()
        # if we have id==-1 there is no point running this on other notebooks
        if tabgroup.id == -1:
            event = QMouseEvent(QEvent.MouseButtonRelease, QPoint(0,0), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)        
            #self.mouseReleaseEvent(event)
            QCoreApplication.postEvent(self,event)
        else:
            # Update all notebooks in the tab group, as they may all be poorly rendered
            for instance in tabgroup.widget_list:
                event = QMouseEvent(QEvent.MouseButtonRelease, QPoint(0,0), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)        
                #instance.tab_bar.mouseReleaseEvent(event)
                QCoreApplication.postEvent(instance.tab_bar,event)

    def find_notebook_index(self):
        return self.tab_widget.get_tab_widget_group().widget_list.index(self.tab_widget)
        
    def setCurrentIndex(self,index):
        widget = self.tab_widget.widget(index)
        return_val = QTabBar.setCurrentIndex(self,index)
        self.fix_displayed_tab(self.find_notebook_index(),None,widget)
        return return_val
                
class TabWidgetGroup:
    def __init__(self,id):
        self.widget_list = []
        self.moving_tab_data = None
        self.id = id
        
    def add_tab_widget(self, widget):
        if widget not in self.widget_list:
            self.widget_list.append(widget)
            
    def remove_tab_widget(self,widget):
        if widget not in self.widget_list:
            return False
            
        if self.moving_tab_data:
            raise Exception('A tab group (id:%d) is being changed while a drag operation is in progress'%self.id)
        
        self.widget_list.remove(widget)
        return True
        

class DragDropTabWidget(QTabWidget):

    instances = {}

    def __init__(self,id=-1):
        QTabWidget.__init__(self)
        self.setAcceptDrops(True)         
        self.tab_bar = DragDropTabBar(self)
        
        self.id = None
        self.setId(id)
        
    def __del__(self):
        self.instances[self.id].remove_tab_widget(self)
    
    def get_tab_widget_group(self):
        return self.instances[self.id]
    
    def setId(self,id):
        # if the id is already set, remove it from the existing tab group
        if self.id:
            self.instances[self.id].remove_tab_widget(self)
            
        # Make the id an integer and set the id property
        id = int(id)
        if id >= 0:
            self.id = id
        else:
            self.id = -1
            
        # Make sure the TabWidgetGroup exists...
        self.instances.setdefault(self.id,TabWidgetGroup(self.id))
        # Add the current TabWidget to the group
        self.instances[self.id].add_tab_widget(self)
        
    def Id(self):
        return self.id
    
    def dragMoveEvent(self, e):
        self.tab_bar.dragMoveEvent(e)
    
    def dragLeaveEvent(self, e):
        self.tab_bar.dragLeaveEvent(e)
    
    def dragEnterEvent(self, e):
        self.tab_bar.dragEnterEvent(e)
    
    def dropEvent(self, e):
        self.tab_bar.dropEvent(e)
        
if __name__ == '__main__':    
    class ViewPort(object):
        def __init__(self, id, container_layout,i):
            #ui = QUiLoader().load('viewport.ui')
            self.tab_widget = DragDropTabWidget(id)
            container_layout.addWidget(self.tab_widget)
            self.tab_widget.addTab(QLabel("foo %d"%i), 'foo')
            self.tab_widget.addTab(QLabel("bar %d"%i), 'bar')
            self.tab_widget.tabBar().setTabTextColor(0,"red")
            self.tab_widget.tabBar().setTabTextColor(1,"green")
            
            
    class RunViewer(object):
        def __init__(self):
            # Load the gui:
            self.moving_tab = None
            self.moving_tab_index = -1
            
            self.window = QWidget()
            container = QVBoxLayout(self.window)
            
            self.viewports = []
            for i in range(3):               
                viewport = ViewPort(3,container,i)
                self.viewports.append(viewport)
            #button = QPushButton("launch iPython")
            #button.clicked.connect(embed)
            #ui.verticalLayout_6.addWidget(button)
            
            self.window.show()
        

    qapplication = QApplication([])
    app = RunViewer()
    sys.exit(qapplication.exec_())


