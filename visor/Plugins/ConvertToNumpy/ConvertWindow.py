from PyQt5.QtWidgets import QMainWindow,QMessageBox,QFileDialog,qApp
from PyQt5.QtCore import QDirIterator,QFileInfo,QDir,qInfo,pyqtSlot
from PyQt5 import uic
import Plugins.ConvertToNumpy.FunctionsConvertWindow as fcw
import os

class Plugin(QMainWindow):

    def __init__(self,args):
        QMainWindow.__init__(self,None)
        ui_convertwindow, _ = uic.loadUiType("./Plugins/ConvertToNumpy/convertwindow.ui")
        self.ui = ui_convertwindow()
        self.ui.setupUi(self)
        self.format=0
        self.ui.actionNPY.setChecked(True)
        self.workspace=args[3]


    #Controla si se pulsa el boton de buscar directorio a convertir
    @pyqtSlot()
    def on_btnCaptureBrowse_clicked(self):
        fileName=QFileDialog.getExistingDirectory(self,self.tr("Open Folder"), self.workspace,QFileDialog.ShowDirsOnly or QFileDialog.DontResloveSymlinks)
        if fileName != None:
            info1=QFileInfo(fileName)
            info2=info1.absoluteDir()
            self.ui.captureFolder.setText(fileName)
            self.ui.outputFile.setText(info2.absoluteFilePath("file"))

    #Controla si se pulsa el fichero en el que se va a realizar la conversión a numpy
    @pyqtSlot()
    def on_btnNumpyBrowser_clicked(self):
        fileName=QFileDialog.getSaveFileName(self,self.tr("Export to numpy"),self.workspace,self.tr("Numpy file (*.npy)"))
        qInfo(fileName[0])
        if fileName[0] != None:
            self.ui.outputFile.setText(fileName[0])

    #Controla si se pulsa el botón de convertir
    @pyqtSlot()
    def on_btnConvert_clicked(self):
        if self.ui.checkBox.isChecked():
            list_dir = os.listdir(self.ui.captureFolder.text())
            print(list_dir)
            for dir in list_dir:
                self.ui.outputFile.setText(self.ui.captureFolder.text()+"/file_"+dir)
                print(self.ui.captureFolder.text()+'/'+dir)
                if fcw.convertFolder(self.ui.captureFolder.text()+'/'+dir+"/capture",self.ui.outputFile.text(),self.ui.normalize.isChecked(),self.ui.inpGain.value(),self.format):
                    Msgbox=QMessageBox()
                    Msgbox.setText("Conversion "+dir+ " succesful!")
                    Msgbox.exec()
                else:
                    Msgbox=QMessageBox()
                    Msgbox.setText("Conversion "+dir+ " to numpy failed!")
                    Msgbox.exec()
        else:
            print(self.ui.outputFile.text())
            if fcw.convertFolder(self.ui.captureFolder.text(),self.ui.outputFile.text(),self.ui.normalize.isChecked(),self.ui.inpGain.value(),self.format):
                Msgbox=QMessageBox()
                Msgbox.setText("Conversion succesful!")
                Msgbox.exec()
            else:
                Msgbox=QMessageBox()
                Msgbox.setText("Conversion to numpy failed!")
                Msgbox.exec()
    #Activa la casilla de normalizar, si es pulsada
    def on_normalize_toggled(self):
        self.ui.inpGain.setEnabled(not self.ui.normalize.isChecked())

    #Controla si se pulsa el botón batch, y si se pulsa convierte el fichero ENVI, con la diferencia que guarda el fichero 
    # resultante en el directorio Padre del directorio introducido
    @pyqtSlot()
    def on_btnBatch_clicked(self):
        it=QDirIterator(self.ui.captureFolder.text(),["DARKREF*.raw"],QDir.Filter.Files,QDirIterator.IteratorFlag.Subdirectories)
        while it.hasNext():
            fileInfo=QFileInfo(it.next())
            capFolder=fileInfo.absoluteDir()
            baseFolder=fileInfo.absoluteDir()
            baseFolder.cdUp()

            print(baseFolder.absolutePath(),capFolder.absolutePath())

            destinationFile=baseFolder.absoluteFilePath("file")
            if self.ui.normalize.isChecked():
                destinationFile=baseFolder.absoluteFilePath("file-norm")

            source=capFolder.absolutePath()

            qInfo(" - "+source+"\n")
            qInfo(" = "+destinationFile+"\n")

            if self.convertFolder(source,destinationFile,self.ui.normalize.isChecked(),self.ui.inpGain.value()):
                self.ui.statusBar.showMessage(baseFolder.dirName()+" converted")
            else:
                self.ui.statusBar.showMessage(baseFolder.dirName()+" failed to convert")

            qApp.processEvents()

        self.ui.statusBar.showMessage("Done!")

    @pyqtSlot()
    def on_actionNPY_triggered(self):
        self.format=0
        self.updateFormat()
    @pyqtSlot()
    def on_actionNPZ_triggered(self):
        self.format=1
        self.updateFormat()
    def updateFormat(self):
        self.ui.actionNPY.setChecked(self.format==0)
        self.ui.actionNPZ.setChecked(self.format==1)






