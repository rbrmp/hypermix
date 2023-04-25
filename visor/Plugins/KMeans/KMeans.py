from PyQt5.QtWidgets import QMainWindow,QFileDialog
from PyQt5.QtCore import Qt, QPoint,pyqtSlot, qInfo
from PyQt5.QtGui import QPixmap
from Graphics_view_zoom import Graphics_view_zoom as zoom
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import * 
import numpy as np
from sklearn.cluster import KMeans
import MainFunctions as func
import Enums
from matplotlib import cm
import KeyEventHandler
import ast


class Plugin(QMainWindow):

    def __init__(self, args):
        QMainWindow.__init__(self,parent=None)
        ui_rmse, _ = uic.loadUiType("./Plugins/KMeans/kmeans.ui")
        self.ui = ui_rmse()
        self.ui.setupUi(self)
        self.params = {}
        self.use_params = False
        self.act_clmap = False
        self.clmap_pred = None
        self.scene_clmap = None
        self.ori_data = args[0]
        self.data = self.ori_data[0]
        self.image = args[1]
        self.user_channel_order = args[2]
        self.clmap = cm.get_cmap('jet')
        self.ui.bt_show_clmap.clicked.connect(self.show_classification_map)
        self.ui.channelSlider.setHidden(False)
        self.ui.channelLabel.setHidden(False)
        self.ui.channelSlider.setValue(0)
        self.ui.channelLabel.setText("Channel: "+str(self.ui.channelSlider.value()))
        self.ui.channelSlider.setMaximum(self.ori_data.shape[3] - 1)
        self.ui.channelSlider.setEnabled(True)
        self.ui.actionExport_clmap_as_png.triggered.connect(self.save_image_png)

        handler=KeyEventHandler.KeyEventHandler(self.ui.graphicsView)
        self.ui.graphicsView.installEventFilter(handler)
        handler.mousePressed.connect(lambda event: self.mousePressEvent(event, 1))
        self.ui.graphicsView.setMouseTracking(True)

        handler2=KeyEventHandler.KeyEventHandler(self.ui.graphics_clmap)
        self.ui.graphics_clmap.installEventFilter(handler2)
        handler2.mousePressed.connect(lambda event: self.mousePressEvent(event, 2))
        self.ui.graphics_clmap.setMouseTracking(True)

        scene = func.load(True, "", None, self.ori_data, self.ui.channelSlider.value())
        self.ui.graphicsView.centerOn(0,0)
        self.ui.graphicsView.setScene(scene)
        self.ui.graphicsView.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.km = KMeans()
        self.ui.params.setText(str(self.km.get_params())[2:-1].replace(", '",", ").replace("':",":").replace(":","="))


    def showEvent(self, event):
        self.resizeEvent(event)

    def show_classification_map(self):
        if self.km != None:
            self.km = KMeans()
            self.clmap_pred = None
            self.act_clmap = False
        
        shapeOriginal = self.data.shape
        self.data = self.data.reshape(-1, self.data.shape[-1])
        self.calculate_kmeans(shapeOriginal)
        if self.clmap_pred is not None: 
            pred = np.reshape(self.clmap_pred,(1, self.clmap_pred.shape[0], self.clmap_pred.shape[1], 1))
            self.scene_clmap, image = func.render_channel(0, 0, pred, Enums.ChannelOrder.H_W_C, self.clmap, None)
            self.ui.graphics_clmap.setScene(self.scene_clmap)
            self.showEvent(None)
            self.data = self.ori_data[0]
        

    def calculate_kmeans(self, orShape):
        try:
            params = ast.literal_eval("{'"+self.ui.params.text()
                                                  .replace(", ",", '").replace(":","':").replace("=","':")+"}")
        except:
            func.showMessage("Error in value of parameters")
            return
        try:
            self.km.set_params(**params)
        except Exception as e:
            func.showMessage(str(e), title="PARAMETERS ARE INCORRECT")
            return
        try:
            self.km.fit(self.data)
        except Exception as e:
            func.showMessage(str(e), title="PARAMETERS ARE INCORRECT")
            return
        self.clmap_pred = self.km.predict(self.data).reshape(orShape[0], orShape[1])
        self.act_clmap = True


    def mousePressEvent(self, event, posMouse=None):
        print(event, posMouse)
        if posMouse != None:
            if posMouse == 1:   img_coord_pt = self.ui.graphicsView.mapToScene(event.pos())
            elif posMouse == 2: img_coord_pt = self.ui.graphics_clmap.mapToScene(event.pos())
            pos = QPoint(int(img_coord_pt.x()), int(img_coord_pt.y()))
            information = "PIXEL SELECTED: ("+str(pos.x())+", "+str(pos.y())+") ["
            
            if posMouse == 1:   information += str(self.ori_data[0, pos.x(), pos.y(), self.ui.channelSlider.value()])
            elif posMouse == 2: information += str(self.clmap_pred[pos.x(), pos.y()])
            information += "]"
                                
            if posMouse == 1:   self.ui.label_image1.setText(information)
            elif posMouse == 2: self.ui.label_image2.setText(information)
            print(information)
            self.ui.graphics_clmap.repaint()
            self.update()

    def on_channelSlider_valueChanged(self, value):
        scene = func.load(True, "", None, self.ori_data, value)
        self.ui.graphicsView.setScene(scene)
        self.showEvent(None)
        self.ui.channelLabel.setText("Channel: "+str(self.ui.channelSlider.value()))


    def save_image_png(self):
        if self.act_clmap:
            fileName=QFileDialog.getSaveFileName(self,self.tr("Export to PNG"),"Capture (name without extension)", self.tr("PNG image (*.png)"))
            qInfo("Export to PNG...")
            if fileName[0] != "" and not self.image.isNull():
                # Get the size of your graphicsview
                rect = self.ui.graphics_clmap.viewport().size()
                # Create a pixmap the same size as your graphicsview
                # You can make this larger or smaller if you want.
                pixmap = QPixmap(rect)
                self.ui.graphics_clmap.viewport().render(pixmap)
                # Render the graphicsview onto the pixmap and save it out.
                pixmap.save(str(fileName[0]) + '.png')
                qInfo("Done!")
            else:
                qInfo("Cancel...")
            

    @pyqtSlot()
    def resizeEvent(self,event):
        scene = self.ui.graphicsView.scene()
        if scene != None:
            bounds=self.ui.graphicsView.scene().itemsBoundingRect()
            self.ui.graphicsView.fitInView(bounds, Qt.AspectRatioMode.KeepAspectRatio)
            self.ui.graphicsView.centerOn(0,0)

        scene = self.ui.graphics_clmap.scene()
        if scene != None:
            bounds=self.ui.graphics_clmap.scene().itemsBoundingRect()
            self.ui.graphics_clmap.fitInView(bounds,Qt.AspectRatioMode.KeepAspectRatio)
            self.ui.graphics_clmap.centerOn(0,0)
        
    
