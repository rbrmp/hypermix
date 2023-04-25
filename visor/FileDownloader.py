from PyQt5.QtCore import QObject,QUrl,pyqtSignal
from PyQt5.QtNetwork import QNetworkAccessManager,QNetworkRequest,QNetworkReply

class FileDownloader(QObject):

    downloaded=pyqtSignal()

    def __init__(self,imageUrl:QUrl,parent=None):
        QObject.__init__(self,parent)
        self.m_WebCtrl=QNetworkAccessManager()
        self.m_DownloadedData=""

        request = QNetworkRequest(imageUrl)

        self.m_WebCtrl.finished.connect(self.fileDownloaded)

        self.m_WebCtrl.get(request)

    
    def fileDownloaded(self,pReply):
        er= pReply.error()

        if er == QNetworkReply.NetworkError.NoError:
            bytes=pReply.readAll()
            self.m_DownloadedData=str(bytes,'utf-8')
            self.downloaded.emit()
        else:
            print("Error ocurred: ", er)
            print(pReply.errorString())


    def downloadedData(self):
        return self.m_DownloadedData
            
            
