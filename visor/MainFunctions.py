import Enums
import numpy as np
from PIL import Image
from PyQt5.QtGui import QPixmap, QImage, QColor
from PyQt5.QtWidgets import QGraphicsScene, QMessageBox, QInputDialog
from PyQt5.QtCore import qInfo, QFileInfo, QDirIterator
import os
from matplotlib import cm
from matplotlib import cm

def render_channel(batch_index,channel_index,data,channel_order,cmap,colorMode):
    np.seterr(divide='ignore', invalid='ignore')

    max_pixel = np.amax(data)
    min_pixel = np.amin(data)

    slope = 255 / (max_pixel - min_pixel)

    if channel_order == Enums.ChannelOrder.H_W_C:
        bitmap1=(data[batch_index,:,:,channel_index] - min_pixel) * slope
    elif channel_order == Enums.ChannelOrder.C_H_W:
        bitmap1=(data[batch_index,channel_index,:,:] - min_pixel) * slope
    else:
        bitmap1=(data[batch_index,:,channel_index,:] - min_pixel) * slope

    bitmap1=(bitmap1 - np.min(bitmap1)) / (np.max(bitmap1 - np.min(bitmap1)))
    
    image = Image.fromarray(np.uint8(cmap(bitmap1)*255))

    image1 = image.toqimage()
    item   = QPixmap(QPixmap.fromImage(image1))
    scene  = QGraphicsScene()
    scene.addPixmap(item)

    return scene, image1

def render3Channels(batch_index,data,channel_order,colorMode,image,bands):
    max_pixel = np.amax(data)
    min_pixel = np.amin(data)

    if len(bands) != 0:
        red,green,blue=selectColorsBand(bands)
    else:
        red,green,blue=0,1,2

    slope = 255 / (max_pixel - min_pixel)

    if channel_order == Enums.ChannelOrder.H_W_C:
        bitmap1=(data[batch_index,:,:,red] - min_pixel) * slope
        bitmap2=(data[batch_index,:,:,green] - min_pixel) * slope
        bitmap3=(data[batch_index,:,:,blue] - min_pixel) * slope
        height,width=bitmap1.shape[0],bitmap1.shape[1]
    elif channel_order == Enums.ChannelOrder.C_H_W:
        bitmap1=(data[batch_index,red,:,:] - min_pixel) * slope
        bitmap2=(data[batch_index,green,:,:] - min_pixel) * slope
        bitmap3=(data[batch_index,blue,:,:] - min_pixel) * slope
        height,width=bitmap1.shape[0],bitmap1.shape[1]
    else:
        bitmap1=(data[batch_index,:,red,:] - min_pixel) * slope
        bitmap2=(data[batch_index,:,green,:] - min_pixel) * slope 
        bitmap3=(data[batch_index,:,blue,:] - min_pixel) * slope
        height,width=bitmap1.shape[1],bitmap1.shape[0]  
    bitmap1=bitmap1.astype(int).flatten(order='C')
    bitmap2=bitmap2.astype(int).flatten(order='C')
    bitmap3=bitmap3.astype(int).flatten(order='C')

    image = QImage(width, height,QImage.Format.Format_RGB888)
    for i in range(len(bitmap1)):
        if colorMode == Enums.ColorMode.RGB:
            image.setPixelColor(int(i%width), int(i/width), 
            QColor(bitmap1[i],bitmap2[i],bitmap3[i]))
        elif colorMode == Enums.ColorMode.BGR:
            image.setPixelColor(int(i%width), int(i/width), 
            QColor(bitmap3[i],bitmap2[i],bitmap1[i]))
        else:
            image.setPixelColor(int(i%width), int(i/width), 
            QColor(bitmap2[i],bitmap3[i],bitmap1[i]))
    
    item = QPixmap(QPixmap.fromImage(image))
    scene = QGraphicsScene()
    scene.addPixmap(item)

    return scene,image

def selectColorsBand(bands):
    red,green,blue=700.0, 548.1, 435.8
    inR=(np.abs(bands-red)).argmin()
    inG=(np.abs(bands-green)).argmin()
    inB=(np.abs(bands-blue)).argmin()

    return inR,inG,inB

#Carga del fichero numpy
def load_file(path,parent,user_channel_order,key=None):
    _, lower=os.path.splitext(path)
    arr:np.ndarray=[]
    bands:np.array=[]
    items=[]
    qInfo("Load numpy")
    if path=="":
        print("Cancel...")
        return None,None,None,None,None,None,None
    if lower == ".npz":
        arr_key=np.load(path)
        if len(arr_key.files) == 1:
            arr=np.load(path)[arr_key.files[0]]
        else:
            if key!= None:
                arr=np.load(path)[key]
                if 'bands' in arr_key.files:   bands=np.load(path)['bands'] 
            else:
                for i in arr_key.files: 
                    if len(np.load(path)[i].shape) >= 2:    items.append(i)
                return None,None,None,None,None,None,items

    elif lower == ".npy":
        arr = np.load(path)
    else:
        fileHdr=QFileInfo(path)
        it=QDirIterator(fileHdr.absolutePath())
        last=fileHdr.fileName().rfind(".")
        name=fileHdr.fileName()[0:last]
        darkHdr = None; whiteHdr = None; dataHdr = None ; whiteData=None; darkData=None
        while it.hasNext():
            fileInfo = QFileInfo(it.next())
            if fileInfo.fileName().__contains__("DARKREF"):
                if fileInfo.fileName().__contains__("hdr"):
                    darkHdr=fileInfo.absoluteFilePath()
                else:
                    darkData=fileInfo.absoluteFilePath()
            elif fileInfo.fileName().__contains__("WHITEREF"):
                if fileInfo.fileName().__contains__("hdr"):
                    whiteHdr=fileInfo.absoluteFilePath()
                else:
                    whiteData=fileInfo.absoluteFilePath()
            elif fileInfo.fileName().startswith(name) and fileInfo.fileName() != fileHdr.fileName():
                dataHdr = fileInfo.absoluteFilePath()
        if dataHdr != None:
            arr = envi_open([fileHdr.absoluteFilePath(), dataHdr], [darkHdr,darkData], [whiteHdr,whiteData])
            if 'wavelength' in read_envi_hdr(fileHdr):
                bands = read_envi_hdr(fileHdr)['wavelength']
                if len(bands) != 0:
                    bands = np.array([float(w) for w in bands])
        else:
            print("MENSAJE DE ERROR DICIENDO QUE NO ESTÁ EL FICHERO DE DATOS")

    num_dimensions = len(arr.shape)

    if num_dimensions < 1:
        msgBox=QMessageBox()
        msgBox.setText("This numpy array does not have any dimensions, expecting at least 1")
        msgBox.exec()
        return
    elif num_dimensions < 2:
        height       = 1
        width        = 1
        num_channels = int(arr.shape[0])
        batch_size   = 1
        arr=np.reshape(arr,(batch_size,height,width,num_channels))
    elif num_dimensions == 2:
        qInfo("Array is 2d, assuming 1 channel")
        height       = int(arr.shape[0])
        width        = int(arr.shape[1])
        num_channels = 1
        batch_size   = 1
        arr=np.reshape(arr,(batch_size,height,width,num_channels))
    elif user_channel_order == Enums.ChannelOrder.C_H_W and num_dimensions == 3:
        qInfo("Rendering as channels*height*width")
        height       = int(arr.shape[1])
        width        = int(arr.shape[2])
        num_channels = int(arr.shape[0])
        batch_size   = 1
        arr=np.reshape(arr,(batch_size,height,width,num_channels))
        arr=np.transpose(arr,(0,3,1,2))
    elif user_channel_order == Enums.ChannelOrder.C_H_W and num_dimensions >= 4:
        qInfo("Rendering as n*channels*height*width")
        height       = int(arr.shape[2])
        width        = int(arr.shape[3])
        num_channels = int(arr.shape[1])
        batch_size   = int(arr.shape[0])
        arr=np.reshape(arr,(batch_size,height,width,num_channels))
        arr=np.transpose(arr,(0,3,1,2))
    elif user_channel_order == Enums.ChannelOrder.H_W_C and num_dimensions == 3:
        qInfo("Rendering as height*width*channels")
        height       = int(arr.shape[0])
        width        = int(arr.shape[1])
        num_channels = int(arr.shape[2])
        batch_size   = 1
        arr=np.reshape(arr,(batch_size,height,width,num_channels))
    elif user_channel_order == Enums.ChannelOrder.H_W_C and num_dimensions >= 4:
        qInfo("Rendering as n*height*width*channels")
        height       = int(arr.shape[1])
        width        = int(arr.shape[2])
        num_channels = int(arr.shape[3])
        batch_size   = int(arr.shape[0])
        arr=np.reshape(arr,(batch_size,height,width,num_channels))
    elif user_channel_order == Enums.ChannelOrder.W_C_H and num_dimensions == 3:
        qInfo("Rendering as height*width*channels")
        height       = int(arr.shape[2])
        width        = int(arr.shape[0])
        num_channels = int(arr.shape[1])
        batch_size   = 1
        arr=np.reshape(arr,(batch_size,height,width,num_channels))
        arr=np.transpose(arr,(0,2,3,1))
    elif user_channel_order == Enums.ChannelOrder.W_C_H and num_dimensions >= 4:
        qInfo("Rendering as n*height*width*channels")
        height       = int(arr.shape[3])
        width        = int(arr.shape[1])
        num_channels = int(arr.shape[2])
        batch_size   = int(arr.shape[0])
        arr=np.reshape(arr,(batch_size,height,width,num_channels))
        arr=np.transpose(arr,(0,2,3,1))
    else:
        msgBox=QMessageBox()
        msgBox.setText("This numpy array is not understood")
        msgBox.exec()
        return
    return arr,bands,height,width,num_channels,batch_size,None

def read_envi_hdr(pathfile):
    wavevalues = ''; metadata = {}; wlen=False
    for line in open(pathfile, 'r'):
        line = line.strip().strip('\n').strip('\r')
        if 'samples =' in line:                           metadata['samples'] = int(line.split('=')[1])
        elif 'lines =' in line:                           metadata['lines'] = int(line.split('=')[1])
        elif 'bands =' in line and 'default' not in line: metadata['bands'] = int(line.split('=')[1])
        elif 'data type =' in line:                       metadata['datatype'] = int(line.split('=')[1])
        elif 'interleave =' in line:                      metadata['interleave'] = line.split('=')[1]
        elif 'wavelength =' in line: wlen=True
        elif wlen and '}' in line:
            metadata['wavelength'] = wavevalues.strip().replace('{','').replace('}','').split(',')
            wlen = False
        elif wlen:                   wavevalues += line
    return metadata


def read_envi_file(pathfile, metadata):
    fd = open(pathfile, 'rb')
    if metadata['datatype'] == 2:    him = np.fromfile(fd, np.int16)
    elif metadata['datatype'] == 4:  him = np.fromfile(fd, np.float32)
    elif metadata['datatype'] == 5:  him = np.fromfile(fd, np.float64)
    elif metadata['datatype'] == 12: him = np.fromfile(fd, np.uint16)
    inter, lines, samples, bands = \
        metadata['interleave'], metadata['lines'], metadata['samples'], metadata['bands']
    if 'bsq' in inter.lower():
        print('Convert BSQ')
        data = np.flipud(np.transpose(him.reshape(bands, samples, lines), (2, 1, 0)))
    elif 'bil' in inter.lower():
        print('Convert BIL')
        data = np.rot90(np.flipud(np.transpose(him.reshape(lines, bands, samples), (2, 0, 1))), k=2)
    elif 'bip' in inter.lower():
        print('Convert BIP')
        data = np.flipud(np.transpose(him.reshape(bands, lines, samples), (1, 2, 0)))
    return data


def envi_open(dataInfo, darkInfo, whiteInfo):
    pathHDR,  pathData  = dataInfo
    darkHDR,  darkData  = darkInfo
    whiteHDR, whiteData = whiteInfo
    arr = read_envi_file(pathData, read_envi_hdr(pathHDR))
    if darkInfo[0] != None and whiteInfo[0] != None:
        metadata = read_envi_hdr(darkHDR)
        darkref  = read_envi_file(darkData, metadata).reshape(metadata['lines'], metadata['samples'], metadata['bands'])
        darknp  = np.ones((metadata['samples'], 1, 1)) * darkref
        metadata = read_envi_hdr(whiteHDR)
        whiteref = read_envi_file(whiteData, metadata).reshape(metadata['lines'], metadata['samples'], metadata['bands'])
        whitenp  = np.ones((metadata['samples'], 1, 1)) * whiteref
        arr      = (arr - darknp) / (whitenp - darknp)
        #arr = np.clip(arr, 0, 1)
    return arr

def load(isNp,path,parent,data,channelValue):
    if not isNp:
        arr,_,_,_,num_channels,_,_= load_file(path,parent,Enums.ChannelOrder.H_W_C)
        if arr is not None:
            if data.shape != arr.shape:
                msgBox=QMessageBox()
                msgBox.setWindowTitle("ERROR LOADING")
                msgBox.setText("The dimensions of the images must be the same.")
                msgBox.exec()
                return
            scene, _ = render_channel(0,channelValue,arr,Enums.ChannelOrder.H_W_C,cm.get_cmap('gray'),Enums.ColorMode.Grayscale)
            return num_channels,arr,scene
    else:
        scene, _ = render_channel(0, channelValue, data, Enums.ChannelOrder.H_W_C,cm.get_cmap('gray'), Enums.ColorMode.Grayscale)
        return scene

def showMessage(message, title=None):
    msgBox=QMessageBox()
    msgBox.setText(message)
    if title != None: msgBox.setWindowTitle(title)
    msgBox.exec()
    return
