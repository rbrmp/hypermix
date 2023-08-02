import sys

import numpy as np
from PyQt5.QtGui import QColor, QTransform, QPen
from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QWidget, QApplication, QGraphicsRectItem, QGraphicsItem, \
    QGraphicsColorizeEffect, QGraphicsView
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSlot, Qt, QPointF
from PyQt5.uic.properties import QtGui, QtCore

app = QApplication(sys.argv)

class MyScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.idBox = 0
        self.numBoxes = 0
        self.opBoxes = np.array([])
        self.current_item = None

    def addBox(self, box):
        box.setId(self.idBox)
        self.idBox = self.idBox + 1
        self.numBoxes = self.numBoxes + 1
        self.opBoxes = np.append(self.opBoxes, box)
        self.addItem(box)
        print("add box, hay ", self.numBoxes)
        print("en el array: ", self.opBoxes.size)

    def deleteBox(self):
        if self.current_item is not None and self.numBoxes > 0:
            index = np.where(self.current_item)
            self.opBoxes = np.delete(self.opBoxes, index)
            self.removeItem(self.current_item)
            self.numBoxes = self.numBoxes - 1

    def deleteAll(self):
        if self.numBoxes > 0:
            self.current_item = None
            self.numBoxes = 0
            self.clear()
            self.opBoxes = np.array([])




    def highlightItem(self):
        pen = QPen(QColor("yellow"), 5)
        self.current_item.setPen(pen)

    def resetItem(self):
        self.current_item.setPen(QPen(QColor(0, 0, 0, 0), 0))

    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        print("touch box ", item)
        if item is not None:
            print("current box none?", self.current_item)
            if self.current_item is None:
                self.current_item = item
                print("current box ", self.current_item)
                self.highlightItem()
            else:
                print("2")
                if self.current_item != item:
                    self.resetItem()
                    self.current_item = item
                    self.highlightItem()
        else:
            if self.current_item is not None: self.resetItem()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.current_item is not None:
            self.current_item.setPos(event.scenePos())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

class Plugin(QMainWindow):
    def __init__(self,args):
        super().__init__()
        self.init_ui()

        # buttons
        self.ui.pushFCLSU.clicked.connect(self.CreateFCLSU)
        self.ui.pushNCLSU.clicked.connect(self.CreateNCLSU)
        self.ui.pushLSU.clicked.connect(self.CreateLSU)
        self.ui.pushISRA.clicked.connect(self.CreateISRA)
        self.ui.pushCLEAR.clicked.connect(self.ClearBox)
        self.ui.pushCLEARALL.clicked.connect(self.ClearScene)


    @pyqtSlot()
    def CreateFCLSU(self):
        box = OpBox(600, 600, 50, 'FCLSU')
        box.setBrush(Qt.red)
        self.scene.addBox(box)

    @pyqtSlot()
    def CreateISRA(self):
        box = OpBox(600, 600, 50, 'ISRA')
        box.setBrush(Qt.blue)
        self.scene.addBox(box)

    @pyqtSlot()
    def CreateLSU(self):
        box = OpBox(600, 600, 50, 'LSU')
        box.setBrush(Qt.black)
        self.scene.addBox(box)

    @pyqtSlot()
    def CreateNCLSU(self):
        box = OpBox(600, 600, 50, 'LSU')
        box.setBrush(Qt.green)
        self.scene.addBox(box)

    @pyqtSlot()
    def ClearBox(self):
        self.scene.deleteBox()

    @pyqtSlot()
    def ClearScene(self):
        self.scene.deleteAll()

    def init_ui(self):
        ui_example, _ = uic.loadUiType("./Plugins/hypermix/hypermix2.ui")
        self.ui = ui_example()
        self.ui.setupUi(self)

        widget = QWidget()
        widget.setLayout(self.ui.VL)
        self.setCentralWidget(widget)

        self.scene = MyScene()
        self.ui.GV.setScene(self.scene)

        # configs
        self.setMinimumSize(400, 300)
        self.ui.GV.setBackgroundBrush(Qt.lightGray)
        self.ui.GV.setDragMode(QGraphicsView.RubberBandDrag)
        self.ui.GV.setInteractive(True)
        self.ui.GV.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.GV.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def eventFilter(self, obj, event):
        # Deshabilitar la política de desplazamiento mientras se mueven los objetos
        if event.type() == QEvent.GraphicsSceneMouseMove and obj.dragMode() == QGraphicsView.RubberBandDrag:
            obj.setInteractive(False)

        # Restaurar la política de desplazamiento después del movimiento
        elif event.type() == QEvent.GraphicsSceneMouseRelease:
            obj.setInteractive(True)

        return super().eventFilter(obj, event)


class OpBox(QGraphicsRectItem):
    def __init__(self, x, y, r, type):
        super().__init__(0, 0, r, r)
        self.setPos(x, y)
        self.type = type
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.id = -1

    def setId(self, newId):
        self.id = newId