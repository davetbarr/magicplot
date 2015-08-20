import numpy
import darc

c = darc.Control('dragon')

def getData(name, nframes):
	return c.GetStreamBlock(name, nframes)[name][0][0]

def getSubApLocation():
	return c.Get('subapLocation')

def processRawPixelData(data):
	side = numpy.sqrt(len(data))
	return data.reshape((side,side))


#data = getData(c, "dragonrtcPxlBuf", 1)
#subApLocation = getSubApLocation(c)
#print data
#print subApLocation
