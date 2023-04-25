from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot

class Plugin(QMainWindow):
    def __init__(self,args):
        QMainWindow.__init__(self,None)
        ui_example, _ = uic.loadUiType("./Plugins/PluginExample/example.ui")
        self.ui = ui_example()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.helloWorld)
        self.ui.label.hide()
    @pyqtSlot()
    def helloWorld(self):
        self.ui.label.setText("HELLO WORLD!")
        self.ui.label.show()