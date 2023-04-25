from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDirIterator,QFileInfo,QDir
import numpy as np
import MainFunctions as mf

#Convierte un fichero ENVI a numpy y lo guarda en un fichero .npz
def convertFolder(source, destination, normalize, pixelGain,format):
    biggestSize     = -1
    biggestFileName = ""
    biggestFile     = ""
    whiteFile       = ""
    darkFile        = ""
    hdrFile         = ""
    darkHdr,darkFile,whiteHdr,whiteFile=None,None,None,None
    it=QDirIterator(source)
    while it.hasNext():
        fileInfo=QFileInfo(it.next())
        if fileInfo.size() > biggestSize and fileInfo.isFile():
            biggestFile     = fileInfo.absoluteFilePath()
            biggestFileName = fileInfo.fileName()
            biggestSize     = fileInfo.size()
        if fileInfo.fileName().__contains__("DARKREF") and not fileInfo.fileName().endswith(".hdr"):  darkFile=fileInfo.absoluteFilePath()
        if fileInfo.fileName().__contains__("WHITEREF") and not fileInfo.fileName().endswith(".hdr"): whiteFile=fileInfo.absoluteFilePath()
    lastindex = biggestFileName.rfind(".")
    rawname   = biggestFileName[0:lastindex]

    it2=QDirIterator(source,["*.HDR"],QDir.Filter.Files)
    while it2.hasNext():
        fileInfo=QFileInfo(it2.next())
        if fileInfo.fileName().startswith(rawname):      hdrFile  = fileInfo.absoluteFilePath()
        if fileInfo.fileName().__contains__("DARKREF"):  darkHdr  = fileInfo.absoluteFilePath()
        if fileInfo.fileName().__contains__("WHITEREF"): whiteHdr = fileInfo.absoluteFilePath()

    reader=mf.read_envi_hdr(hdrFile)
    width = int(reader['samples'])

    if format==1:
        wavelengths=reader['wavelength']

        if len(wavelengths) != 0:
            wavelengths = [float(w) for w in wavelengths]
            wavelengths = np.array(wavelengths)

    if width < 0:
        Msgbox=QMessageBox()
        Msgbox.setText("Could not read HDR file")
        Msgbox.exec()
        return False

    image=mf.envi_open([hdrFile,biggestFile],[darkHdr,darkFile],[whiteHdr, whiteFile])

    if normalize:
        print(" -> Writing normalized numpy array with data...")
        pixelGain = 1
        image     = image / np.linalg.norm(image)
    if pixelGain != 1:
        print(" -> Writing numpy array with data...")
        image = image * int(pixelGain)
    if format==1 and len(wavelengths) != 0:
        np.savez(destination,cube=image,bands=wavelengths)
    else:
        np.save(destination, image)
    print(" ->Conversion Done! ")
    return True