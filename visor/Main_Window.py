import importlib
import Graphics_view_zoom
import FileDownloader
import KeyEventHandler
import Enums
import Histogram
from PyQt5.QtWidgets import QMainWindow,QWidget,QLabel,QMessageBox,QFileDialog
from PyQt5.QtGui import QImage,QMouseEvent
from PyQt5.QtCore import qInfo,QFileInfo,Qt,QUrl, pyqtSlot
from PyQt5 import uic
import numpy as np
import os
import CheckableComboBox as cbx
from matplotlib import cm
import MainFunctions as mf
app_version=6

class MainWindow(QMainWindow):
    def __init__ (self,plugins:list=[]):
        QWidget.__init__(self)
        form_class,_ = uic.loadUiType("./uis/mainwindow.ui")
        self.formUi=form_class()
        self.formUi.setupUi(self)

        self.workspace=""
        self.num_channels      = -1
        self.width             = -1
        self.height            = -1
        self.batch_size        = -1
        self.max_pixel_in_file = -1
        self.min_pixel_in_file = -1
        self.loadedData        = []
        self.loadedDataSelectBands = []
        self.bands=[]
        self.listPluginsActions = []
        self.strPlugins = []
        self.plugins=plugins
        self.charge=True
        self.image             = QImage()
        self.histogram         = Histogram.Histogram(self.workspace)
        self.colorMode           = Enums.ColorMode.Grayscale
        self.user_channel_order  = Enums.ChannelOrder.H_W_C
        self.loaded_path         = ""
        self.cmap=cm.get_cmap('gray')

        self.formUi.actionExport_as_PNG.setEnabled(False)
        self.formUi.actionHistogram.setEnabled(False)
        self.formUi.color_Grayscale.setEnabled(False)
        self.formUi.color_Colormap.setEnabled(False)

        self.formUi.comboBoxColors.setFixedWidth(100)
        self.formUi.comboBoxColors.addItems(['jet','inferno','hot','cool','viridis','cividis'])
        self.formUi.comboBoxColors.currentTextChanged.connect(self.other_colors)
        self.formUi.comboBoxColors.setEnabled(False)

        spacer = QWidget()
        spacer.setFixedWidth(200)

        self.formUi.comboBox.setFixedWidth(100)
        self.formUi.comboBox.currentTextChanged.connect(self.comboboxItemChanged)
        #self.formUi.toolBar.addWidget(self.formUi.comboBox)
        self.formUi.comboBox.setEnabled(False)

        ###SELECCION DE BANDAS###
        self.comboBoxSB = cbx.CheckableComboBox()
        self.comboBoxSB.setFixedWidth(80)
        self.comboBoxSB.setEnabled(False)
        self.formUi.pushButton.setFixedWidth(80)
        self.formUi.pushButton.clicked.connect(self.push_selectButton)
        self.formUi.pushButton.setEnabled(False)

        self.formUi.horizontalLayout.addWidget(self.formUi.toolBar)
        self.formUi.horizontalLayout.addWidget(self.formUi.comboBoxColors)

        self.formUi.horizontalLayout_2.addWidget(self.formUi.toolBar_2)
        self.formUi.horizontalLayout_2.addWidget(self.comboBoxSB)
        self.formUi.horizontalLayout_2.addWidget(self.formUi.pushButton)
        self.formUi.horizontalLayout_2.addWidget(spacer)
        self.formUi.horizontalLayout_2.addWidget(self.formUi.comboBox)

        z = Graphics_view_zoom.Graphics_view_zoom(self.formUi.imageCanvas)
        z.set_modifiers(Qt.KeyboardModifier.NoModifier)

        dimensionLabel = QLabel(self)
        dimensionLabel.setText("")
        self.formUi.statusBar.addPermanentWidget(dimensionLabel, 0)

        handler=KeyEventHandler.KeyEventHandler(self.formUi.imageCanvas)
        self.formUi.imageCanvas.installEventFilter(handler)
        handler.mousePositionChange.connect(self.mouseMovedEvent)
        handler.mousePressed.connect(self.mousePressedEvent)

        imageUrl=QUrl("https://raw.githubusercontent.com/mhaut/TFG-JuanCarmona/main/version.txt?token=GHSAT0AAAAAABU3JRO5ULFWVSNKXFI6SKVMYVVU7AA")
        self.update_checker=FileDownloader.FileDownloader(imageUrl)
        self.update_checker.downloaded.connect(self.version_downloaded)

        self.formUi.imageCanvas.setMouseTracking(True)
        self.updateSettingsMenu()
        self.formUi.channelSlider.setEnabled(False)
        self.formUi.channelLabel.setEnabled(False)
        self.formUi.batchSlider.setEnabled(False)
        self.formUi.batchLabel.setEnabled(False)

        if self.plugins != []:
            self.plug=self.formUi.menuBar.addMenu("Plugins")

    #Actualiza las opciones del menú 
    def updateSettingsMenu(self):
        self.formUi.order_C_H_W.setChecked(    self.user_channel_order == Enums.ChannelOrder.C_H_W)
        self.formUi.order_H_W_C.setChecked(    self.user_channel_order == Enums.ChannelOrder.H_W_C)
        self.formUi.order_W_C_H.setChecked(    self.user_channel_order == Enums.ChannelOrder.W_C_H)

        self.formUi.color_RGB.setEnabled(self.num_channels >= 3)
        self.formUi.color_BGR.setEnabled(self.num_channels >= 3)
        self.formUi.color_GBR.setEnabled(self.num_channels >= 3)


        self.formUi.color_Grayscale.setChecked(self.colorMode == Enums.ColorMode.Grayscale)
        self.formUi.color_Colormap.setChecked(self.colorMode  == Enums.ColorMode.ColorMap)
        self.formUi.color_RGB.setChecked(self.colorMode       == Enums.ColorMode.RGB)
        self.formUi.color_BGR.setChecked(self.colorMode       == Enums.ColorMode.BGR)
        self.formUi.color_GBR.setChecked(self.colorMode       == Enums.ColorMode.GBR)

        self.comboBoxSB.setEnabled(self.colorMode != Enums.ColorMode.RGB and self.colorMode != Enums.ColorMode.BGR and self.colorMode != Enums.ColorMode.GBR and self.num_channels > 1)
        self.formUi.pushButton.setEnabled(self.comboBoxSB.isEnabled())
        self.formUi.comboBoxColors.setEnabled(self.colorMode == Enums.ColorMode.ColorMap)


    #Comprueba si existe una nueva versión para descargar
    @pyqtSlot()
    def version_downloaded(self):
        try:
            data=self.update_checker.downloadedData()
            if len(data) > 0:
                list1 = data.split('|')
                if len(list1) == 2:
                    version=int(list1[0])
                    if version > app_version:
                        text   = "New version avaible!<br> New in this version:" + list1[1]
                        msgBox = QMessageBox()
                        msgBox.setWindowTitle("New version avaible")
                        msgBox.setText(text)
                        msgBox.exec()
                    else:
                        print("No updates required")
        except: 
            print("Could not check for updates")


    #Funciona cuando se pulsa el ratón dentro de la imagen, y si está activo el histograma muestra los datos del espectro del pixel seleccionado
    def mousePressedEvent(self, event:QMouseEvent):
        if not self.image.isNull() and self.formUi.actionHistogram.isChecked():
            img_coord_pt = self.formUi.imageCanvas.mapToScene(event.pos())
            if event.buttons() == Qt.MouseButton.LeftButton : new=False
            else:   new=True
            x, y = int(img_coord_pt.x()), int(img_coord_pt.y())
            n = self.formUi.batchSlider.value()

            if x <= self.width and y <= self.height and y >= 0 and x >= 0:
                    self.histogram.setData(self.loadedData,new,n,x,y,self.num_channels,self.user_channel_order)
                    self.histogram.show()
                    self.histogram.activateWindow()


    #Funciona cuando se mueve el cursor del ratón en la imagen y controla si se pulsa o no dentro de la imagen
    def mouseMovedEvent(self,event):
        if not self.image.isNull():
            img_coord_pt = self.formUi.imageCanvas.mapToScene(event.pos())

            x=int(img_coord_pt.x())
            y=int(img_coord_pt.y())
            n=self.formUi.batchSlider.value()

            channelSelected = self.formUi.channelSlider.value()

            if x >= 0 and x < self.width and y >= 0 and y < self.height: 
                message=""
                if self.user_channel_order == Enums.ChannelOrder.H_W_C:
                    value=self.loadedData[n,y,x,channelSelected]
                    message=("("+ str(x) + ", " + str(y) +") ["+ str(value) +"]")
                elif self.user_channel_order == Enums.ChannelOrder.C_H_W:
                    value=self.loadedData[n,channelSelected,y,x]
                    message=("("+ str(x) + ", " + str(y) +") ["+ str(value) +"]")
                else:
                    value=self.loadedData[n,x,channelSelected,y]
                    message=("("+ str(x) + ", " + str(y) +") ["+ str(value) +"]")
                self.formUi.statusBar.showMessage(message)

                if event.buttons() == Qt.MouseButton.LeftButton or event.buttons() == Qt.MouseButton.RightButton:
                    self.mousePressedEvent(event)

    #Carga del fichero numpy
    def load(self, path,key=None,inComboNpz=False):
        self.on_order_H_W_C_triggered()
        arr,bands,height,width,num_channels,batch_size,items=mf.load_file(path,self,self.user_channel_order,key)
        self.loaded_path=path
        if arr is not None:
            self.formUi.actionExport_as_PNG.setEnabled(True)
            self.formUi.actionHistogram.setEnabled(True)
            self.formUi.color_Grayscale.setEnabled(True)
            self.formUi.color_Colormap.setEnabled(True)
        ###### PLUGINS ########
            if self.loadedData != []:
                for act in self.plug.actions(): self.plug.removeAction(act)
            for p in self.plugins:
                if os.path.isdir("./Plugins/"+p) and p != "PluginExample":
                    files=os.listdir("./Plugins/"+p)
                    for f in files:
                        if f.endswith(".py") and not f.__contains__("Functions"):
                            module=f[:-3]
                            self.strPlugins.append("Plugins."+p+"."+module)
                            action=self.plug.addAction(module)
                            self.listPluginsActions.append(action)
                            action.setCheckable(True)
                            action.triggered.connect(self.showPlugin)

            num_dimensions = len(arr.shape)

            self.bands,self.height,self.width,self.num_channels,self.batch_size = bands,height,width,num_channels,batch_size
            self.formUi.batchSlider.setValue(0)
            self.formUi.channelSlider.setValue(0)
            self.updateTextInToolBar()
            self.charge=True

            self.loadedData=arr
            self.loadedDataSelectBands=self.loadedData
            self.max_pixel_in_file=np.amax(self.loadedData)
            self.min_pixel_in_file=np.amin(self.loadedData)

            self.histogram = Histogram.Histogram(self.workspace)
            self.histogram.setMax(self.max_pixel_in_file)
            self.histogram.setMin(self.min_pixel_in_file)

            qInfo("Max pixel value in file "+str(self.max_pixel_in_file)+", Min pixel value in file "+str(self.min_pixel_in_file))
            message="Channels: "+str(self.num_channels)+" Width: "+str(self.width)+" Height: "+str(self.height)
            qInfo(message)
            self.formUi.statusBar.showMessage(message)

            self.updateSettingsMenu()

            self.formUi.channelSlider.setEnabled((self.num_channels <= 1 or self.colorMode == Enums.ColorMode.RGB or self.colorMode==Enums.ColorMode.BGR or self.colorMode==Enums.ColorMode.GBR)==False)
            self.formUi.channelLabel.setEnabled(self.formUi.channelSlider.isEnabled())

            self.formUi.channelSlider.setMaximum(self.num_channels - 1)

            self.formUi.batchSlider.setEnabled(num_dimensions > 3 and self.batch_size > 1)
            self.formUi.batchLabel.setEnabled(self.formUi.batchSlider.isEnabled())
            self.formUi.batchSlider.setMaximum(self.batch_size - 1)

            info = QFileInfo(path)
            self.setWindowTitle(info.fileName())

            self.updateTextInToolBar()
            self.comboBoxSB.setEnabled(True)
            self.formUi.pushButton.setEnabled(True)

            self.render(self.bands)
            
            self.comboBoxSB.clear()
            items = map(str, range(self.num_channels))
            self.comboBoxSB.addItems(items)

            qInfo("Done!")
            self.resizeEvent(None)
        if not inComboNpz :
            self.formUi.comboBox.clear()
            self.formUi.comboBox.setEnabled(False)
        if items != None :
            self.formUi.comboBox.setEnabled(True)
            self.formUi.comboBox.addItems(items)



    def render(self,bands,valueChannel=None,valueBatch=None,fromPushSelectButton=False):
        if valueChannel == None:    valueChannel=self.formUi.channelSlider.value()
        if valueBatch == None:    valueBatch=self.formUi.batchSlider.value()
        if self.colorMode == Enums.ColorMode.RGB or self.colorMode==Enums.ColorMode.BGR or self.colorMode==Enums.ColorMode.GBR:
            scene,self.image=mf.render3Channels(valueBatch,self.loadedData,self.user_channel_order,self.colorMode,self.image,bands)
            self.formUi.imageCanvas.setScene(scene)
        else:
            scene,self.image=mf.render_channel(valueBatch,valueChannel,self.loadedDataSelectBands,self.user_channel_order,self.cmap,self.colorMode)
            self.formUi.imageCanvas.setScene(scene)
            self.formUi.pushButton.setEnabled(self.comboBoxSB.isEnabled())
        self.formUi.channelSlider.setEnabled((self.num_channels <= 1 or self.colorMode == Enums.ColorMode.RGB or self.colorMode==Enums.ColorMode.BGR or self.colorMode==Enums.ColorMode.GBR)==False)
        self.formUi.channelLabel.setEnabled(self.formUi.channelSlider.isEnabled())

        # if not fromPushSelectButton:
        #     self.comboBoxSB.clear()
        #     items = map(str, range(self.num_channels))
        #     self.comboBoxSB.addItems(items)

    #Redimensiona la imagen
    @pyqtSlot()
    def resizeEvent(self,event):
        scene=self.formUi.imageCanvas.scene()
        if scene != None:
            bounds=self.formUi.imageCanvas.scene().itemsBoundingRect()
            self.formUi.imageCanvas.fitInView(bounds,Qt.AspectRatioMode.KeepAspectRatio)
            self.formUi.imageCanvas.centerOn(0,0)
        if event != None:
            event.accept()

    #Actualiza la etiqueta de los scroll Batch y Channel
    def updateTextInToolBar(self):
        if self.batch_size > 1 and self.num_channels <= 1:
            self.formUi.batchLabel.setText("Batch: "+str(self.formUi.batchSlider.value()))
        elif self.batch_size > 1 and self.num_channels > 1:
            self.formUi.batchLabel.setText("Batch: "+str(self.formUi.batchSlider.value()))
            self.formUi.channelLabel.setText("Channel: "+str(self.formUi.channelSlider.value()))
        else:
            self.formUi.channelLabel.setText("Channel: "+str(self.formUi.channelSlider.value()))
    
    #Controla si hay algún cambio en el slider de los canales y si lo hay lo actualiza
    def on_channelSlider_valueChanged(self,value):
        self.render(self.bands,valueChannel=value)
        self.updateTextInToolBar()

    #Controla si hay algún cambio en el slider de los batch y si lo hay lo actualiza
    def on_batchSlider_valueChanged(self,value):
        self.render(self.bands,valueBatch=value)
        self.resizeEvent(None)
        self.updateTextInToolBar()

    #Controla si se pulsa la opción de abrir fichero numpy.
    @pyqtSlot()
    def on_actionOpen_triggered(self):
        fileName = QFileDialog.getOpenFileName(self, self.tr("Open Image"), self.workspace, "File (*.npy *.npz *.hdr)")
        if fileName != None:
            self.load(str(fileName[0]))
    
    #Controla si se pulsa la opción de abrir exportar la imagen a formato PNG.
    @pyqtSlot()
    def on_actionExport_as_PNG_triggered(self):
        fileName=QFileDialog.getSaveFileName(self,self.tr("Export to PNG"),self.workspace+"/Capture (name without extension)", self.tr("PNG image (*.png)"))
        qInfo("Export to PNG...")
        if fileName[0] != "" and not self.image.isNull():
            self.image.save(str(fileName[0]) + '.png')
            qInfo("Done!")
        else:
            qInfo("Cancel...")


    #Comprueba si recibe un evento para cerrar la ventana del histograma.
    @pyqtSlot()
    def closeEvent(self, event):
        self.histogram.close()
        if event != None:
            event.accept()
    
    #Controla si se recibe una acción sobre el histograma cuando este no está activo.
    @pyqtSlot()
    def on_actionHistogram_triggered(self):
        if not self.formUi.actionHistogram.isChecked():
            self.histogram = Histogram.Histogram(self.workspace)
            self.histogram.setMax(self.max_pixel_in_file)
            self.histogram.setMin(self.min_pixel_in_file)
    @pyqtSlot()
    def comboboxItemChanged(self):
        if self.formUi.comboBox.currentText() != "":   self.load(self.loaded_path,self.formUi.comboBox.currentText(),True)

    def chargePlugins(self):
        self.charge=False
        if self.strPlugins != []:
            self.instancePlugins=[]
            for p in self.strPlugins:
                self.instancePlugins.append(importlib.import_module(p,".").Plugin([self.loadedData, self.image,self.user_channel_order,self.workspace]))

    #Controla si se pulsa la opción de convertir ENVI a numpy
    @pyqtSlot()
    def showPlugin(self):
        if self.charge: self.chargePlugins()
        if len(self.loadedData) != 0:
            for plug in zip(self.listPluginsActions,self.instancePlugins):
                if plug[0].isChecked():
                    plug[1].show()
            for p in self.listPluginsActions:
                p.setChecked(False)
        else: 
            for plug in self.listPluginsActions: plug.setChecked(False)

    @pyqtSlot()
    def push_selectButton(self):
        if len(self.comboBoxSB.currentData()) != 0:
            self.loadedDataSelectBands=self.loadedData

            item = [int(x) for x in self.comboBoxSB.currentData()]
            num_channels=len(item)
            if self.user_channel_order == Enums.ChannelOrder.H_W_C:  arr=self.loadedDataSelectBands[:,:,:,item]
            elif self.user_channel_order == Enums.ChannelOrder.C_H_W:    arr=self.loadedDataSelectBands[:,item,:,:]
            else:   arr=self.loadedDataSelectBands[:,:,item,:]

            self.formUi.channelSlider.setMaximum(num_channels - 1)
            self.formUi.channelSlider.setEnabled(True)
            self.formUi.channelSlider.setValue(0)
            self.loadedDataSelectBands = arr    
            
            self.render(self.bands,fromPushSelectButton=True)

            msgBox=QMessageBox()
            msgBox.setWindowTitle("Channels Selected")
            msgBox.setText("Selected "+str(item)+" Channels")
            msgBox.exec()

            #self.loadedDataSelectBands = arr   
    def updateWindow(self,color=None):
        if color != None:
            self.cmap=cm.get_cmap(color)
        self.updateSettingsMenu()
        self.loadedDataSelectBands=self.loadedData
        self.render(self.bands)
        self.formUi.channelSlider.setMaximum(self.num_channels - 1)
        self.formUi.channelSlider.setEnabled(True)

    def updateChannelOrder(self,channelOrder,nC,h,w):
        self.user_channel_order  = channelOrder
        self.formUi.channelSlider.setValue(0)
        self.num_channels=self.loadedData.shape[nC]
        self.height=self.loadedData.shape[h]
        self.width=self.loadedData.shape[w]
        self.updateWindow()
        self.formUi.actionHistogram.setChecked(False)
        self.histogram.close()
        self.comboBoxSB.clear()
        items = map(str, range(self.num_channels))
        self.comboBoxSB.addItems(items)

    #Controla si se selecciona la opción C*H*W, como ordenación de canales.
    @pyqtSlot()
    def on_order_C_H_W_triggered(self):
        if len(self.loadedData) != 0:
            qInfo("Set to mode C*H*W")
            self.updateChannelOrder(Enums.ChannelOrder.C_H_W,1,2,3)
        else:   self.formUi.order_C_H_W.setChecked(False)

    #Controla si se selecciona la opción H*W*C, como ordenación de canales.
    @pyqtSlot()
    def on_order_H_W_C_triggered(self):
        if len(self.loadedData) != 0:
            qInfo("Set to mode H*W*C")
            self.updateChannelOrder(Enums.ChannelOrder.H_W_C,3,1,2)
        else:   self.formUi.order_H_W_C.setChecked(False)

    #Controla si se selecciona la opción W*C*H, como ordenación de canales.
    @pyqtSlot()
    def on_order_W_C_H_triggered(self):
        if len(self.loadedData) != 0:
            qInfo("Set to mode W_C_H")
            self.updateChannelOrder(Enums.ChannelOrder.W_C_H,2,3,1)
        else:   self.formUi.order_W_C_H.setChecked(False)

    #Controla si se selecciona la opción Grayscale, para mostrar la imagen.
    @pyqtSlot()
    def on_color_Grayscale_triggered(self):
        if len(self.loadedData) != 0:
            self.colorMode = Enums.ColorMode.Grayscale
            self.updateWindow('gray')
        else:   self.formUi.color_Grayscale.setChecked(False)

    #Controla si se selecciona la opción Colormap, para mostrar la imagen.
    @pyqtSlot()
    def on_color_Colormap_triggered(self):
        if len(self.loadedData) != 0:
            qInfo("Colormap triggered")
            self.colorMode = Enums.ColorMode.ColorMap
            self.updateWindow('jet')
            self.formUi.comboBoxColors.setCurrentText('jet')
        else:   self.formUi.color_Colormap.setChecked(False)

    @pyqtSlot()
    def other_colors(self):
        color=self.formUi.comboBoxColors.currentText()
        qInfo(color+" triggered")
        self.colorMode = Enums.ColorMode.ColorMap
   

        self.updateWindow(color)  
    #Controla si se selecciona la opción RGB, para mostrar la imagen. 
    @pyqtSlot()
    def on_color_RGB_triggered(self):
        if self.num_channels >= 3 :
            self.colorMode = Enums.ColorMode.RGB
        self.loadedDataSelectBands=self.loadedData
        self.render(self.bands)
        self.formUi.pushButton.setEnabled(False)
        self.updateSettingsMenu()

    @pyqtSlot()
    def on_color_BGR_triggered(self):
        if self.num_channels >= 3 :
            self.colorMode = Enums.ColorMode.BGR 
        self.loadedDataSelectBands=self.loadedData
        self.render(self.bands)
        self.formUi.pushButton.setEnabled(False)
        self.updateSettingsMenu()

    @pyqtSlot()
    def on_color_GBR_triggered(self):
        if self.num_channels >= 3 :
            self.colorMode=Enums.ColorMode.GBR
        self.loadedDataSelectBands=self.loadedData
        self.render(self.bands)
        self.formUi.pushButton.setEnabled(False)
        self.updateSettingsMenu()
    @pyqtSlot()
    def on_actionSet_Workspace_triggered(self):
        self.workspace=QFileDialog.getExistingDirectory(self,"Set the workspace")
