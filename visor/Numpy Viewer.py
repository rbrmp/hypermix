import Main_Window as mw
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import Qt
import sys
from qt_material import apply_stylesheet
import os

if __name__ == "__main__":
    QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    plugins = os.listdir("./Plugins")
    w = mw.MainWindow(plugins)

    extra = {
    # Density Scale
    'density_scale': '-2',
    }

    apply_stylesheet(app, theme='dark_purple.xml',extra=extra)

    w.show()
    sys.exit(app.exec_())
