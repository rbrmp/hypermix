from PyQt5.QtWidgets import QMainWindow,QFileDialog, QWidget, QVBoxLayout
from PyQt5.QtChart import QChartView,QChart,QValueAxis,QLineSeries
from PyQt5.QtCore import Qt,qInfo
from PyQt5.QtGui import QPainter,QImage
import Enums
import KeyEventHandler
import numpy as np
from PyQt5 import uic


class Histogram(QMainWindow):

    def __init__(self,workspace:str,parent=None):
        QMainWindow.__init__(self,parent=parent)
        self.chartView = QChartView()
        self.chartView2= QChartView()
        self.chartView3= QChartView()
        self.chart     = QChart()
        self.chartDifferenceBands = QChart()
        self.chartDifferencePixel = QChart()
        self.axisX     = QValueAxis()
        self.axisXDB     = QValueAxis()
        self.axisXDP     = QValueAxis()
        self.axisY     = QValueAxis()
        self.axisYDB    = QValueAxis()
        self.axisYDP    = QValueAxis()
        self.baseSelected=[]
        self.base=[]
        self.newPush=True
        self.base_data           = QLineSeries()
        self.differenciated_data = QLineSeries()
        self.differenciated_pixels = []

        self.workspace=workspace

        self.max_value=-1
        self.min_value=-1
        self.numPixelsSelect=1

        ui_histogram, _ = uic.loadUiType("./uis/histogram.ui")
        self.ui = ui_histogram()
        self.ui.setupUi(self)

        self.chartView = QChartView(self)
        
        self.chart.legend().hide()
        self.chart.setTitle("Spectrogram")

        self.chart.addAxis(self.axisX, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axisY, Qt.AlignmentFlag.AlignLeft)

        self.chartView.setChart(self.chart)
        self.chartView.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.chart.addSeries(self.base_data)

        ######################################################################

        self.chartView2 = QChartView(self)
        
        self.chartDifferenceBands.legend().hide()
        self.chartDifferenceBands.setTitle("Radiometric Precision")

        self.chartDifferenceBands.addAxis(self.axisXDB, Qt.AlignmentFlag.AlignBottom)
        self.chartDifferenceBands.addAxis(self.axisYDB,Qt.AlignmentFlag.AlignLeft)

        self.chartView2.setChart(self.chartDifferenceBands)
        self.chartView2.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.chartDifferenceBands.addSeries(self.differenciated_data)

        ######################################################################

        self.chartView3 = QChartView(self)
        
        self.chartDifferencePixel.legend().hide()
        self.chartDifferencePixel.setTitle("Pixel Difference")

        self.chartDifferencePixel.addAxis(self.axisXDP, Qt.AlignmentFlag.AlignBottom)
        self.chartDifferencePixel.addAxis(self.axisYDP,Qt.AlignmentFlag.AlignLeft)

        self.chartView3.setChart(self.chartDifferencePixel)
        self.chartView3.setRenderHint(QPainter.RenderHint.Antialiasing)

        for i in self.differenciated_pixels: self.chartDifferencePixel.addSeries(i)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.lay = QVBoxLayout(central_widget)
        self.lay.addWidget(self.chartView,stretch=3)
        self.lay.addWidget(self.chartView2,stretch=2)
        self.lay.addWidget(self.chartView3,stretch=2)

        #######################################
        handler = KeyEventHandler.KeyEventHandler(self.chartView)
        self.chartView.installEventFilter(handler)
        handler.mouseDoubleClicked.connect(self.mouseDoubleClickedEvent)
        ######################################        
        handler2 = KeyEventHandler.KeyEventHandler(self.chartView2)
        self.chartView2.installEventFilter(handler2)
        handler2.mouseDoubleClicked.connect(self.mouseDoubleClickedEvent2)
        ######################################        
        handler3 = KeyEventHandler.KeyEventHandler(self.chartView3)
        self.chartView3.installEventFilter(handler3)
        handler3.mouseDoubleClicked.connect(self.mouseDoubleClickedEvent3)

    def saveImage(self,filename,chartView,event):
        if filename != "":
            image=QImage(chartView.sceneRect().size().toSize(), QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.transparent)
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            chartView.render(painter)
            image.save(filename + '.png')
            del painter
        else: print("Cancel...")
        if event !=None:
            event.accept()

    #Controla si se pulsa dos veces dentro de la ventana del histograma y si es así guarda el histograma como imagen
    def mouseDoubleClickedEvent(self,event):
        filename=QFileDialog.getSaveFileName(self,"Export to PNG", "", "PNG image(*.png)")
        qInfo(str(filename[0]))
        self.saveImage(filename[0],self.chartView,event)

    def mouseDoubleClickedEvent2(self,event):
        filename=QFileDialog.getSaveFileName(self,"Export to PNG", "", "PNG image(*.png)")
        qInfo(str(filename[0]))
        self.saveImage(filename[0],self.chartView2,event)
    def mouseDoubleClickedEvent3(self,event):
        filename=QFileDialog.getSaveFileName(self,"Export to PNG", "", "PNG image(*.png)")
        qInfo(str(filename[0]))
        self.saveImage(filename[0],self.chartView3,event)

    def setMax(self, maximo):
        self.max_value = maximo


    def setMin(self, minimo):
        self.min_value = minimo


    #Crea las gráficas que ofrece la clase Histograma, tanto el espectro del pixel como la diferencia de las bandas.
    def setData(self, dataPtr, new, n, x, y, num_channels, channelOrder):
        if new:
            if not self.newPush:
                self.baseSelected.append(self.base)
                base_data           = QLineSeries()
                differenciated_data = QLineSeries()
                self.base_data, self.differenciated_data = base_data, differenciated_data
                self.chart.addSeries(self.base_data)
                self.chartDifferenceBands.addSeries(self.differenciated_data)
                self.numPixelsSelect+=1
                self.newPush=True
        else :
            data,differentiated,differentiatedPixel,max           = QLineSeries(),QLineSeries(),[],0
            if channelOrder == Enums.ChannelOrder.H_W_C:
                self.base = dataPtr[n,y,x,:].flatten()
            elif channelOrder == Enums.ChannelOrder.C_H_W:
                self.base = dataPtr[n,:,y,x].flatten()
            else:
                self.base = dataPtr[n,x,:,y].flatten()
            diff = (self.base[1:] / self.base[:-1])
            diff[~np.isfinite(diff)] = 0

            self.base=np.array(self.base,dtype=np.float64)
            if self.numPixelsSelect > 1:
                for i in range(self.numPixelsSelect-1):
                    diffP = self.base / self.baseSelected[i]
                    dP=QLineSeries()
                    for j, (p) in enumerate(diffP): 
                        dP.append(j,p)
                        if p > max: max = p
                    differentiatedPixel.append(dP)

            for i, (a,d) in enumerate(zip(self.base, diff)):
                data.append(i, a)
                differentiated.append(i, d)
            
            self.axisX.setRange(0, num_channels-1)
            self.axisXDB.setRange(0, num_channels-1)
            self.axisXDP.setRange(0, num_channels-1)
            self.axisY.setRange(0, self.max_value)
            self.axisYDB.setRange(0,2)
            self.axisYDP.setRange(0,max)

            self.chart.removeSeries(self.base_data)
            self.base_data           = data
            self.chart.addSeries(self.base_data)
            data.attachAxis(self.axisX)
            data.attachAxis(self.axisY)

            self.chartDifferenceBands.removeSeries(self.differenciated_data)
            self.differenciated_data = differentiated
            self.chartDifferenceBands.addSeries(self.differenciated_data)
            differentiated.attachAxis(self.axisXDB)
            differentiated.attachAxis(self.axisYDB)

            if self.numPixelsSelect > 1:
                for i in self.differenciated_pixels:    self.chartDifferencePixel.removeSeries(i)
                self.differenciated_pixels = differentiatedPixel
                for i in self.differenciated_pixels:    
                    self.chartDifferencePixel.addSeries(i)
                    i.attachAxis(self.axisXDP)
                    i.attachAxis(self.axisYDP)
            self.newPush=False
