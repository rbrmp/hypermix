from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import QObject,QEvent,pyqtSignal
class KeyEventHandler(QObject):

    mouseDoubleClicked=pyqtSignal(QMouseEvent)
    mousePressed=pyqtSignal(QMouseEvent)
    mouseReleased=pyqtSignal(QMouseEvent)
    mousePositionChange=pyqtSignal(QMouseEvent)
    def __init__(self,parent=None):
        QObject.__init__(self,parent=parent)

    def eventFilter(self, obj=QObject, event=QEvent):
        res=True
        if   event.type() == QEvent.Type.MouseButtonDblClick:
            self.mouseDoubleClicked.emit(QMouseEvent(event))
        elif event.type() == QEvent.Type.MouseButtonPress:
            self.mousePressed.emit(QMouseEvent(event))
        elif event.type() == QEvent.Type.MouseButtonRelease:
            self.mouseReleased.emit(QMouseEvent(event))
        elif event.type() == QEvent.Type.MouseMove:
            self.mousePositionChange.emit(QMouseEvent(event))
        else:
            res = QObject.eventFilter(self,obj, event)
        return res
