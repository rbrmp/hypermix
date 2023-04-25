from PyQt5.QtWidgets import QWidget, QGraphicsScene,QFileDialog
from PyQt5.QtCore import Qt, QPoint, QRect, QSize, pyqtSlot, qInfo
from PyQt5.QtGui import QPainter, QImage, QPixmap, QPen, QColor
from Graphics_view_zoom import Graphics_view_zoom as zoom
from PyQt5 import uic
import numpy as np
from PIL import Image as im


class Plugin(QWidget):
    def __init__(self,args):
        QWidget.__init__(self,parent=None)
        ui_masking, _ = uic.loadUiType("./Plugins/Clipping/clipping.ui")
        self.ui = ui_masking()
        self.ui.setupUi(self)

        self.image=args[1]
        self.workspace=args[3]
        self.copy=QImage()
        self.data=None

        z = zoom(self.ui.graphicsView)
        z.set_modifiers(Qt.KeyboardModifier.NoModifier)

        tam = QSize(350, 350)
        self.image = self.image.scaled(tam)
        
        self.begin, self.destination = QPoint(), QPoint()
        self.ui.maskButton.clicked.connect(self.push_maskButton)
        self.ui.saveButton.clicked.connect(self.saveAsNumpyFile)
        self.ui.saveButton.setEnabled(False)

    @pyqtSlot()
    def push_maskButton(self):
        item = QPixmap(QPixmap.fromImage(self.copy))
        scene = QGraphicsScene()
        scene.addPixmap(item)
        self.ui.graphicsView.setScene(scene)
        self.resizeEvent(None)

        self.ui.saveButton.setEnabled(True)
    
    @pyqtSlot()
    def resizeEvent(self,event):
        scene=self.ui.graphicsView.scene()
        if scene != None:
            bounds=self.ui.graphicsView.scene().itemsBoundingRect()
            self.ui.graphicsView.fitInView(bounds,Qt.AspectRatioMode.KeepAspectRatio)
            self.ui.graphicsView.centerOn(0,0)
        if event != None:
            event.accept()

    @pyqtSlot()
    def saveAsNumpyFile(self):
        if self.copy.height() > 0 and self.copy.width() > 0:
            image=im.fromqimage(self.copy)
            self.data = np.array(image.getdata()).reshape(image.size[1], image.size[0],4)
            fileName=QFileDialog.getSaveFileName(self,self.tr("Save as numpy file"),self.workspace, self.tr("(*.npy)"))
            qInfo("Save as numpy file...")
            if fileName[0] != "":
                np.save(str(fileName[0]),self.data)
                qInfo("Done!")
            else:
                qInfo("Cancel...")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(20, 20, self.image)
        imageBegin, imageDestination = QPoint(20,20), QPoint(self.image.width()+20,self.image.height()+20)
        marginsX = (self.begin.x() >= imageBegin.x() and self.begin.x() < imageDestination.x()) and (self.destination.x() < imageDestination.x() and self.destination.x() >= imageBegin.x())
        marginsY = (self.begin.y() >= imageBegin.y() and self.begin.y() < imageDestination.y()) and (self.destination.y() < imageDestination.y() and self.destination.y() >= imageBegin.y())
        
        if not self.begin.isNull() and not self.destination.isNull() and marginsX and marginsY:
            rect = QRect(self.begin, self.destination)
            painter.setPen(QPen(QColor(255, 0, 0),3))
            painter.drawRect(rect.normalized())

    def mousePressEvent(self, event):
        if event.buttons() and Qt.LeftButton:
            self.begin = event.pos()
            self.destination = self.begin
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton:
            self.destination = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        bx,by,dx,dy=self.begin.x()-20,self.begin.y()-20,self.destination.x()-20,self.destination.y()-20
        w=abs(dx - bx) 
        h=abs(dy - by)
        if bx < dx and by < dy:
            self.copy= self.image.copy(bx,by,w,h)
        elif bx > dx and by > dy:
            self.copy= self.image.copy(dx,dy,w,h)
        elif bx > dx and by < dy:
            self.copy= self.image.copy(dx,by,w,h)
        elif bx < dx and by > dy:
            self.copy= self.image.copy(bx,dy,w,h)