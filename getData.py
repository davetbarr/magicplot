import numpy
import darc
import pyqtgraph
from PyQt4 import QtCore, QtGui

c = darc.Control()

def getData(name, nframes, callback=None, decimation=None):
	return c.GetStreamBlock(name, nframes, callback=callback, decimate=decimation)

def getSubApLocation():
	return c.Get('subapLocation')

def getSubApFlag():
	return c.Get('subapFlag')

def rectFromSubAp(array):
	left, top, width, height = array[3], array[0], array[1]-array[0], array[4]-array[3]
	return QtCore.QRectF(left, top, width, height)

def getSubApRects():
	subApArray = getSubApLocation()
	subApFlags = getSubApFlag()
	rectList = []
	for i in range(subApArray.shape[0]):
		if subApFlags[i] == 0:
			continue
		else:
			rectList.append(rectFromSubAp(subApArray[i,:]))
	return rectList

def squareRawPixelData(data):
	side = numpy.sqrt(len(data))
	square =  data.reshape((side,side))
	flipped = numpy.fliplr(square)
	return numpy.rot90(flipped)

def getRefCentroids():
	return c.Get('refCentroids')

#data = getData(c, "dragonrtcPxlBuf", 1)
#subApLocation = getSubApLocation()
#test = getSubApRects(subApLocation)
#print data
#print subApLocation
