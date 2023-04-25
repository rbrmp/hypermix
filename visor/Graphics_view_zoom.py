import PyQt5
from PyQt5.QtWidgets import QApplication,QGraphicsView,QSlider
from PyQt5.QtCore import pyqtSignal,QPointF,QObject,Qt,QEvent,qDebug,QPoint
import PyQt5.QtGui

class Graphics_view_zoom(QObject):
    zoomed=pyqtSignal() 
    def __init__(self,view1:QGraphicsView):
        QObject.__init__(self,view1)
        self.view=view1
        self.view.viewport().installEventFilter(self)
        self.view.setMouseTracking(True)
        self.modifiers = Qt.KeyboardModifier.ControlModifier
        self.zoom_factor_base=1.0015
        self.horizontal_scroll_accumulator=0

        self.target_scene_pos    = QPointF()
        self.target_viewport_pos = QPointF()
        

    def gentle_zoom(self,factor):

        self.view.scale(float(factor),float(factor))
        self.view.centerOn(self.target_scene_pos)
        delta_viewport_pos= self.target_viewport_pos - QPointF(self.view.viewport().width() / 2.0, self.view.viewport().height() / 2.0)

        viewport_center = self.view.mapFromScene(self.target_scene_pos) - delta_viewport_pos
        self.view.centerOn(self.view.mapToScene(viewport_center.toPoint()))
        self.zoomed.emit()
        
    def set_modifiers(self, modifier):
        self.modifiers=modifier

    def set_zoom_factor_base(self,factor):
        self.zoom_factor_base=factor

    def eventFilter(self,object, event:QEvent):

        if event.type() == QEvent.Type.MouseMove:
            mouseEvent=PyQt5.QtGui.QMouseEvent(event)
            delta=QPointF()
            delta = self.target_viewport_pos - mouseEvent.pos()
            if abs(delta.x()) > 5 or abs(delta.y()) > 5:
                self.target_viewport_pos = mouseEvent.pos()
                self.target_scene_pos = self.view.mapToScene(mouseEvent.pos())
        
        else:
            if event.type() == QEvent.Type.Wheel:
                wheelEvent=PyQt5.QtGui.QWheelEvent(event)
                keyboardModifier=QApplication.keyboardModifiers()

                vertical_angle=wheelEvent.angleDelta().y()
                horizontal_angle=wheelEvent.angleDelta().x()

                if QApplication.keyboardModifiers() == self.modifiers:
                    if abs(vertical_angle) > 0:
                        factor=pow(self.zoom_factor_base,vertical_angle)
                        
                        self.gentle_zoom(factor)
                        return True
                
                if abs(horizontal_angle) > 0:
                    if QApplication.keyboardModifiers() and Qt.KeyboardModifier.ShiftModifier:
                        horizontal_angle *=3
                    
                    parentWidget= self.view.parent()
                    batchSlider = parentWidget.findChild(QSlider,"batchSlider")
                    oldBatchValue = batchSlider.value()

                    degrees_per_item=15
                    scroll_pseudovalue_per_item = 8* degrees_per_item

                    self.horizontal_scroll_accumulator += horizontal_angle

                    diffValue=(self.horizontal_scroll_accumulator / scroll_pseudovalue_per_item)

                    self.horizontal_scroll_accumulator -= diffValue * scroll_pseudovalue_per_item

                    newValue = oldBatchValue + diffValue
                    batchSlider.setValue(newValue)

                    qDebug("BatchSlider: " + batchSlider + "; Horizontal Angle: " + horizontal_angle
                        + "; oldValue: " + oldBatchValue +"; newValue: " + newValue + "; remaining accumulator value: " + self.horizontal_scroll_accumulator
                        + "; Keyboard Modifier: " << keyboardModifier)

                    return True

        return False
        
    


