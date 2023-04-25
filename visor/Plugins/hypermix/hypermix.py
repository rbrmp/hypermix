import sys

import numpy as np
from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QWidget, QApplication, QGraphicsRectItem, QGraphicsItem
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSlot, Qt, QPointF
from PyQt5.uic.properties import QtGui, QtCore

app = QApplication(sys.argv)

class Plugin(QMainWindow):
    def __init__(self,args):
        super().__init__()
        self.init_ui()
        self.opBoxes = np.empty(0)

        # buttons
        self.ui.pushFCLSU.clicked.connect(self.CreateFCLSU)
        self.ui.pushNCLSU.clicked.connect(self.CreateNCLSU)
        self.ui.pushLSU.clicked.connect(self.CreateLSU)
        self.ui.pushISRA.clicked.connect(self.CreateISRA)
        self.ui.pushCLEAR.clicked.connect(self.ClearScene)

    @pyqtSlot()
    def CreateFCLSU(self):
        box = OpBox(600, 600, 50, 'FCLSU')
        box.setBrush(Qt.red)
        self.opBoxes = np.append(self.opBoxes, box)
        self.scene.addItem(box)

    @pyqtSlot()
    def CreateISRA(self):
        box = OpBox(600, 600, 50, 'ISRA')
        box.setBrush(Qt.blue)
        self.opBoxes = np.append(self.opBoxes, box)
        self.scene.addItem(box)

    @pyqtSlot()
    def CreateLSU(self):
        box = OpBox(600, 600, 50, 'LSU')
        box.setBrush(Qt.black)
        self.opBoxes = np.append(self.opBoxes, box)
        self.scene.addItem(box)

    @pyqtSlot()
    def CreateNCLSU(self):
        box = OpBox(600, 600, 50, 'LSU')
        box.setBrush(Qt.green)
        self.opBoxes = np.append(self.opBoxes, box)
        self.scene.addItem(box)

    @pyqtSlot()
    def ClearScene(self):
        #np.clear(self.opBoxes)
        self.scene.clear()

    def init_ui(self):
        ui_example, _ = uic.loadUiType("./Plugins/hypermix/hypermix2.ui")
        self.ui = ui_example()
        self.ui.setupUi(self)

        widget = QWidget()
        widget.setLayout(self.ui.VL)
        self.setCentralWidget(widget)

        self.scene = QGraphicsScene()
        self.ui.GV.setScene(self.scene)

        self.setMinimumSize(400, 300)
        self.ui.GV.setBackgroundBrush(Qt.lightGray)

class OpBox(QGraphicsRectItem):
    def __init__(self, x, y, r, type):
        super().__init__(0, 0, r, r)
        self.setPos(x, y)
        #self.setAcceptHoverEvents(True)
        self.type = type
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def mouseMoveEvent(self, event):
        delta = event.pos() - event.lastPos()
        self.setPos(self.pos() + delta)