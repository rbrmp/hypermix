import MainFunctions as mf
from PyQt5.QtWidgets import QMessageBox
import Enums
from matplotlib import cm
import numpy as np
from numpy import array
from PyQt5.QtCore import QPoint


def load(isNp,path,parent,data,channelValue,batchValue,channelOrder):
    if not isNp:
        arr,_,_,_,num_channels,_,_=mf.load_file(path,parent,channelOrder)
        if arr is not None:
            if data.shape != arr.shape:
                msgBox=QMessageBox()
                msgBox.setWindowTitle("ERROR LOADING")
                msgBox.setText("The dimensions of the images must be the same.")
                msgBox.exec()
                return
            scene, _ = mf.render_channel(batchValue,channelValue,arr,channelOrder,cm.get_cmap('gray'),Enums.ColorMode.Grayscale)
            return num_channels,arr,scene
    else:
        scene, _ = mf.render_channel(batchValue, channelValue, data, channelOrder,cm.get_cmap('gray'), Enums.ColorMode.Grayscale)
        return scene


def calculateMetricsBands(data:array, data1:array, channelValue:int, channel2Value:int, batchValue:int, batch2Value:int, channelOrder:Enums.ChannelOrder) -> str:
    if channelOrder == Enums.ChannelOrder.H_W_C:  p1=data[batchValue,:,:,channelValue]; p2 = data1[batch2Value,:,:,channel2Value]
    elif channelOrder == Enums.ChannelOrder.C_H_W:    p1=data[batchValue,channelValue,:,:]; p2 = data1[batch2Value,channel2Value,:,:]
    else:   p1=data[batchValue,:,channelValue,:]; p2 = data1[batch2Value,:,channel2Value,:]

    MSE  = np.average((p1 - p2) ** 2)
    SAD  = np.sum(np.abs(np.subtract(p1,p2)))
    RMSE = np.sqrt(MSE)
    return "Root Mean Square Error(RMSE): "+str(RMSE)+"\n Mean Square Error(MSE): "+str(MSE)+"\n Sum of absolute difference(SAD): "+str(SAD)

def calculateMetricsDatas(data:array, data1:array) -> str:
    MSE  = np.average((data - data1) ** 2)
    SAD  = np.sum(np.abs(np.subtract(data,data1)))
    RMSE = np.sqrt(MSE)
    return "Root Mean Square Error(RMSE): "+str(RMSE)+"\n Mean Square Error(MSE): "+str(MSE)+"\n Sum of absolute difference(SAD): "+str(SAD)

def calculateMetricsPixels(data:array, data1:array, point1:QPoint, point2:QPoint, batchValue:int, batch2Value:int, channelOrder:Enums.ChannelOrder) -> str:
    if channelOrder == Enums.ChannelOrder.H_W_C:  p1=data[batchValue, point1.y(), point1.x(), :]; p2 = data1[batch2Value, point2.y(), point2.x(),:]; width=data.shape[2]; height=data.shape[1]
    elif channelOrder == Enums.ChannelOrder.C_H_W:    p1=data[batchValue, :,point1.y(), point1.x()]; p2 = data1[batch2Value, :,point2.y(), point2.x()]; width=data.shape[3]; height=data.shape[2]
    else:   p1=data[batchValue, point1.x(),:,point1.y()]; p2 = data1[batch2Value, point2.x(),:,point2.y()]; width=data.shape[1]; height=data.shape[3]

    if point1 != None and point2 != None:
        margins  = point1.x() >= 0 and point1.x() < width  and point1.y() >= 0 and point1.y() < height
        margins1 = point2.x() >= 0 and point2.x() < width and point2.y() >= 0 and point2.y() < height

        if margins and margins1:
            MSE  = np.average((p1 - p2) ** 2)
            SAD  = np.sum(np.abs(np.subtract(p1, p2)))
            RMSE = np.sqrt(MSE)
            return "Root Mean Square Error(RMSE): "+str(RMSE)+"\n Mean Square Error(MSE): "+str(MSE)+"\n Sum of absolute difference(SAD): "+str(SAD)
        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("ERROR")
            msgBox.setText("PIXELS OUT OF RANGE")
            msgBox.exec()
            return
    else:
        return "some point is None"
