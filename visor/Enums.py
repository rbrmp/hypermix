import enum

import numpy as np

class ChannelOrder(enum.Enum):
    H_W_C=0
    C_H_W=1
    W_C_H=2

class ColorMode(enum.Enum):
    Grayscale=0
    ColorMap=1
    RGB=2
    BGR=3
    GBR=4