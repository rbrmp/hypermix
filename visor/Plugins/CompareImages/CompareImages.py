from PyQt5.QtWidgets import QMainWindow,QFileDialog
from PyQt5.QtCore import pyqtSlot,Qt
from PyQt5 import uic
import Plugins.CompareImages.FunctionsCompareImages as func
import KeyEventHandler
from Graphics_view_zoom import Graphics_view_zoom as zoom
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtCore import QPoint
import Enums


class Plugin(QMainWindow):
    def __init__(self,args):
        QMainWindow.__init__(self,parent=None)
        ui_rmse, _ = uic.loadUiType("./Plugins/CompareImages/compareImages.ui")
        self.ui = ui_rmse()
        self.ui.setupUi(self)
        self.height=0
        self.width=0
        self.num_channels=0
        self.data=args[0]
        self.channel_order=args[2]
        self.workspace=args[3]
        self.data1=None
        self.method=0
        self.point1,self.point2=None,None
        z1 = zoom(self.ui.graphicsView)
        z2 = zoom(self.ui.graphicsView_2)
        z1.set_modifiers(Qt.KeyboardModifier.NoModifier)
        z2.set_modifiers(Qt.KeyboardModifier.NoModifier)
        handler1 = KeyEventHandler.KeyEventHandler(self.ui.graphicsView)
        handler2 = KeyEventHandler.KeyEventHandler(self.ui.graphicsView_2)
        self.ui.graphicsView.installEventFilter(handler1)
        self.ui.graphicsView_2.installEventFilter(handler2)
        handler1.mousePressed.connect(self.mousePressEvent1)
        handler2.mousePressed.connect(self.mousePressEvent2)

        self.ui.actionBand.setChecked(True)

        self.ui.channelSlider_2.setEnabled(False)
        self.ui.channelLabel_2.setEnabled(False)
        self.ui.batchSlider_2.setEnabled(False)
        self.ui.batchLabel_2.setEnabled(False)

        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton.clicked.connect(self.results)

        self.scene = func.load( True,"", None, self.data, self.ui.channelSlider.value(),self.ui.batchSlider.value(),self.channel_order)
        self.ui.channelSlider.setValue(0)
        self.ui.channelLabel.setText("Channel: "+str(self.ui.channelSlider.value()))

        if self.channel_order == Enums.ChannelOrder.H_W_C:  self.ui.channelSlider.setMaximum(self.data.shape[3] - 1)
        elif self.channel_order == Enums.ChannelOrder.C_H_W:    self.ui.channelSlider.setMaximum(self.data.shape[1] - 1)
        else:   self.ui.channelSlider.setMaximum(self.data.shape[2] - 1)

        self.ui.batchSlider.setValue(0)
        self.ui.batchLabel.setText("Batch: "+str(self.ui.batchSlider.value()))

        self.ui.batchSlider.setMaximum(self.data.shape[0] - 1)
        self.ui.channelSlider.setEnabled(True)
        self.ui.batchSlider.setEnabled(self.data.shape[0] > 1)
        self.ui.batchLabel.setEnabled(self.ui.batchSlider.isEnabled())

        self.ui.graphicsView.setScene(self.scene)
        self.ui.pushButton.setEnabled(False)
        self.select_scene = None
        self.ellipseItem1 = None
        self.ellipseItem2 = None


    def showEvent(self, event):
        self.resizeEvent(event)

    @pyqtSlot()
    def paintEvent(self, event):
        rad = 0.5
        if self.select_scene == 1:
            if self.ellipseItem1 != None: self.scene.removeItem(self.ellipseItem1)
            self.ellipseItem1 = self.scene.addEllipse(self.point1.x() - rad, self.point1.y() - rad, rad, rad, QPen(QColor(255, 0, 0),1))#, QBrush(Qt::SolidPattern));
        elif self.select_scene == 2:
            if self.ellipseItem2 != None: self.scene2.removeItem(self.ellipseItem2)
            self.ellipseItem2 = self.scene2.addEllipse(self.point2.x() - rad, self.point2.y() - rad, rad, rad, QPen(QColor(255, 0, 0),1))#, QBrush(Qt::SolidPattern));
        else:
            pass # no hay mas escenas


    def mousePressEvent1(self, event):
        if self.method == 2:
            self.select_scene = 1
            img_coord_pt = self.ui.graphicsView.mapToScene(event.pos())
            self.point1 = QPoint(int(img_coord_pt.x()), int(img_coord_pt.y()))
            self.ui.label_image1.setText("PIXEL SELECTED: "+str(self.point1.x())+", "+str(self.point1.y()))
            self.ui.graphicsView.repaint()
            self.update()

    def mousePressEvent2(self, event):
        if self.method == 2:
            self.select_scene = 2
            img_coord_pt = self.ui.graphicsView_2.mapToScene(event.pos())
            self.point2 = QPoint(int(img_coord_pt.x()), int(img_coord_pt.y()))
            self.ui.label_image2.setText("PIXEL SELECTED: "+str(self.point2.x())+", "+str(self.point2.y()))
            self.ui.graphicsView_2.repaint()
            self.update()

    def results(self):
        if self.method == 0:   results = func.calculateMetricsBands(self.data, self.data1, self.ui.channelSlider.value(), self.ui.channelSlider_2.value(),self.ui.batchSlider.value(),self.ui.batchSlider_2.value(),self.channel_order)
        elif self.method == 1: results = func.calculateMetricsDatas(self.data, self.data1)
        elif self.method == 2: results = func.calculateMetricsPixels(self.data, self.data1,self.point1, self.point2,self.ui.batchSlider.value(),self.ui.batchSlider_2.value(),self.channel_order)
        else:                  results = ""
        self.ui.label.setText(results)

    @pyqtSlot()
    def on_actionImage_1_triggered(self):
        fileName = QFileDialog.getOpenFileName(self, self.tr("Open Image"), self.workspace, "File (*.npy *.npz *.hdr)")

        if fileName != "":
            self.ui.channelSlider_2.setValue(0)
            self.ui.channelLabel_2.setText("Channel: "+str(self.ui.channelSlider_2.value()))

            self.ui.batchSlider_2.setValue(0)
            self.ui.batchLabel_2.setText("Batch: "+str(self.ui.batchSlider_2.value()))

            load = func.load(False,str(fileName[0]),self,self.data,self.ui.channelSlider_2.value(),self.ui.batchSlider_2.value(),self.channel_order)
            if load != None:
                self.num_channels,self.data1,self.scene2=load[0],load[1],load[2]
                self.ui.channelSlider_2.setMaximum(self.num_channels - 1)
                self.ui.channelSlider_2.setEnabled(True)
                self.ui.channelLabel_2.setEnabled(True)

                self.ui.batchSlider_2.setEnabled(self.data1.shape[0] > 1)
                self.ui.batchSlider_2.setMaximum(self.data1.shape[0] - 1)
                self.ui.batchLabel_2.setEnabled(self.ui.batchSlider_2.isEnabled())

                self.ui.graphicsView_2.setScene(self.scene2)
                self.ui.pushButton.setEnabled(True)
                self.resizeEvent(None)


    @pyqtSlot()
    def resizeEvent(self,event):
        self.scene = self.ui.graphicsView.scene()
        if self.scene != None:
            bounds=self.ui.graphicsView.scene().itemsBoundingRect()
            self.ui.graphicsView.fitInView(bounds,Qt.AspectRatioMode.KeepAspectRatio)
            self.ui.graphicsView.centerOn(0,0)
        self.scene2 = self.ui.graphicsView_2.scene()
        if self.scene2 != None:
            bounds=self.ui.graphicsView_2.scene().itemsBoundingRect()
            self.ui.graphicsView_2.fitInView(bounds,Qt.AspectRatioMode.KeepAspectRatio)
            self.ui.graphicsView_2.centerOn(0,0)

    def on_channelSlider_valueChanged(self, value):
        self.ellipseItem1 = None
        self.scene = func.load(True, "", None, self.data, value,self.ui.batchSlider.value(),self.channel_order)
        self.ui.graphicsView.setScene(self.scene)
        self.resizeEvent(None)
        self.ui.channelLabel.setText("Channel: "+str(self.ui.channelSlider.value()))

    def on_batchSlider_valueChanged(self, value):
        self.ellipseItem1 = None
        self.scene = func.load(True, "", None, self.data, self.ui.channelSlider.value(),value,self.channel_order)
        self.ui.graphicsView.setScene(self.scene)
        self.resizeEvent(None)
        self.ui.batchLabel.setText("Batch: "+str(self.ui.batchSlider.value()))

    def on_batchSlider_2_valueChanged(self, value):
        self.ellipseItem2 = None
        self.scene2 = func.load(True, "", None, self.data1,self.ui.channelSlider_2.value(),value,self.channel_order)
        self.ui.graphicsView_2.setScene(self.scene2)
        self.resizeEvent(None)
        self.ui.batchLabel_2.setText("Batch: "+str(self.ui.batchSlider_2.value()))

    def on_channelSlider_2_valueChanged(self, value):
        self.ellipseItem2 = None
        self.scene2 = func.load(True, "", None, self.data1, value,self.ui.batchSlider_2.value(),self.channel_order)
        self.ui.graphicsView_2.setScene(self.scene2)
        self.resizeEvent(None)
        self.ui.channelLabel_2.setText("Channel: "+str(self.ui.channelSlider_2.value()))

    def updateMethod(self):
        self.ui.actionBand.setChecked(self.method == 0)
        self.ui.actionComplete_Image.setChecked(self.method == 1)
        self.ui.actionPixelImage.setChecked(self.method == 2)

    @pyqtSlot()
    def on_actionBand_triggered(self):
        self.method=0
        self.ui.label.clear()
        self.ui.label_image1.setEnabled(False)
        self.ui.label_image2.setEnabled(False)
        self.updateMethod()

    @pyqtSlot()
    def on_actionComplete_Image_triggered(self):
        self.method=1
        self.ui.label.clear()
        self.ui.label_image1.setEnabled(False)
        self.ui.label_image2.setEnabled(False)
        self.updateMethod()

    @pyqtSlot()
    def on_actionPixelImage_triggered(self):
        self.method=2
        self.ui.label.clear()
        self.ui.label_image1.setEnabled(True)
        self.ui.label_image2.setEnabled(True)
        self.updateMethod()
