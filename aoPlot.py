import sys
import os
SRC_PATH = os.path.dirname(os.path.abspath(__file__))
os.system("pyuic4 {0}/subscribeWindow.ui > {0}/subscribeWindow_ui.py".format(SRC_PATH))
os.system("pyuic4 {0}/aoPlot.ui > {0}/aoPlot_ui.py".format(SRC_PATH))

import aoPlot_ui
import subscribeWindow_ui

from PyQt4 import QtCore, QtGui
import numpy
from astropy.io import fits
import getData
from dragon.rtc import DataSubscriber
import magicPlot
import getData
import pyqtgraph

class AOPlot(QtGui.QWidget, aoPlot_ui.Ui_AOPlot):
    updateCentSignal = QtCore.pyqtSignal(list, list)
    updateArrowSignal = QtCore.pyqtSignal(list, list, list, list)

    def __init__(self, parent=None):
        super(AOPlot, self).__init__(parent)

        self.setupUi(self)
        self.updateCentSignal.connect(self.plotCents)
        self.updateArrowSignal.connect(self.plotArrows)

        self.isPlottingPixels = False
        self.isPlottingCents = False
        self.isPlottingSubaps = False
        self.isPlottingCalPixels = False
        self.isDrawingArrows = False
        self.isDrawingRefCents = False

        self.mp = magicPlot.MagicPlot(self)
        self.verticalLayout.addWidget(self.mp)

        self.plotSomething.clicked.connect(self.mp.plotRandom1d)
        self.plotSomething2d.clicked.connect(self.mp.plotRandom2d)
        #Subscribe window
        self.subSelect = SubscribeWindow()

        self.subSelect.checkPixels.toggled.connect(self.checkPixelsHandler)
        self.subSelect.checkCalPixels.toggled.connect(self.checkCalPixelsHandler)
        self.subSelect.checkCents.toggled.connect(self.checkCentsHandler)
        self.subSelect.checkSubaps.toggled.connect(self.checkSubapsHandler)
        self.subSelect.checkPlotPixels.toggled.connect(self.checkPlotPixelsHandler)
        self.subSelect.checkPlotCalPixels.toggled.connect(self.checkPlotCalPixelsHandler)
        self.subSelect.checkPlotCents.toggled.connect(self.checkPlotCentsHandler)
        self.subSelect.checkPlotSubaps.toggled.connect(self.checkPlotSubapsHandler)

        self.subSelect.show()

        # Threads from dragonAPI (from gui_TAS.py)
        self.pixelThread = UpdateThread('pixels', 10)
        self.pixelThread.updateSignal.connect(self.updatePixels)
        self.pixelThread.subscribeFailedSig.connect(self.subscribeFailed)
        self.calPixelThread = UpdateThread('calPixels', 10)
        self.calPixelThread.updateSignal.connect(self.updateCalPixels)
        self.calPixelThread.subscribeFailedSig.connect(self.subscribeFailed)
        self.centThread = UpdateThread('cents', 10)
        self.centThread.updateSignal.connect(self.updateCents)
        self.centThread.subscribeFailedSig.connect(self.subscribeFailed)
        self.subapsThread = UpdateThread('subaps', 10)
        self.subapsThread.updateSignal.connect(self.updateSubaps)
        self.subapsThread.subscribeFailedSig.connect(self.subscribeFailed)

    def subscribeFailed(self):
        print "subscribe failed"

    def checkPixelsHandler(self, checked):
        if checked:
            print "pixel subscription started"
            self.pixelThread.start() #starts entire thread run()
        else:
            print "pixel subscription stopped"
            self.pixelThread.stopSubscription() #only stops sub, not entire thread

    def checkCalPixelsHandler(self, checked):
        if checked:
            print "cal pixel subscription started"
            self.calPixelThread.start()
        else:
            print "cal pixel subscription stopped"
            self.calPixelThread.stopSubscription()

    def checkCentsHandler(self, checked):
        if checked:
            print "cents subscription started"
            self.centThread.start()
        else:
            print "cents subscription stopped"
            self.centThread.stopSubscription()

    def checkSubapsHandler(self, checked):
        if checked:
            print "subaps subscription started"
            # I've put the subaps stream in darcWrapper and in DARC_STREAMS
            # in dragonAPI.py, so this works
            # Haven't done anything to dummyDarc though so that doesn't work
            self.subapsThread.start()

        else:
            print "subaps subscription stopped"
            self.subapsThread.stopSubscription()

    def checkPlotPixelsHandler(self, checked):
        self.isPlottingPixels = checked

    def checkPlotCalPixelsHandler(self, checked):
        self.isPlottingCalPixels = checked

    def checkPlotCentsHandler(self, checked):
        self.isPlottingCents = checked

    def checkPlotSubapsHandler(self, checked):
        self.isPlottingSubaps = checked

    def updatePixels(self, data):
        # Find new way of processing raw pixels?
        # Fix flickering when both Cal and Raw pixels streaming
        self.data = getData.squareRawPixelData(data[2][0])
        if self.isPlottingPixels and not self.isPlottingCalPixels:
            self.plotPixels(self.data)
        else:
            try:
                self.mp.plotItem.clear()
            except AttributeError:
                pass

    def updateCalPixels(self, data):
        # Find new way of processing raw pixels?
        self.data = getData.squareRawPixelData(data[2][0])
        if self.isPlottingCalPixels and not self.isPlottingPixels:
            self.plotCalPixels(self.data)
        else:
            try:
                self.mp.plotItem.clear()
            except AttributeError:
                pass

    def updateCents(self, data):
        self.cents = data[2][0]
        centlist = []
        centrePoints = []
        index = numpy.arange(len(self.cents), step=2)
        for i in index:
            centlist.append(QtCore.QPointF(self.cents[i],self.cents[i+1]))
        for j in self.subapRects:
            centrePoints.append(j.center())
        self.centCoOrds = numpy.array(centlist)+numpy.array(centrePoints)
        if self.isPlottingCents:
            # Work out a way of plotting 1d and 2d, like this (but better):
            if self.mp.plotMode == 1:
                self.mp.plotView.disableAutoRange()
                self.mp.plotObj.setData(self.cents)
                return None
            else:
                self.plotCents(self.centCoOrds)
        else:
            try:
                self.mp.centPlot.clear()
            except AttributeError:
                pass

    def updateSubaps(self, data):
        self.subaps = data[2][0].reshape((49,6))  # need to find way of reshaping
        self.subapRects = []                      # maybe get subapLocation?
        subapFlag = getData.getSubapFlag()
        for i, flag in enumerate(subapFlag):
            if flag == 0:
                continue
            else:
                self.subapRects.append(getData.rectFromSubap(self.subaps[i,:]))
        if self.isPlottingSubaps:
            self.plotSubaps(self.subapRects)
        else: #clear the subaps if they are drawn
            try:
                self.mp.subapPlot.clear()
            except AttributeError:
                pass

    def plotPixels(self, data):
        self.mp.plot(data)

    def plotCalPixels(self, data):
        self.mp.plot(data)

    def plotCents(self, data):
        self.mp.plotMode = 2
        try:
            self.mp.centPlot.clear()
        except AttributeError:
            self.mp.centPlot = pyqtgraph.ScatterPlotItem()
            self.mp.centPlot.setPen(QtGui.QPen(QtCore.Qt.green))
            self.mp.centPlot.setBrush(QtGui.QColor("lime"))
            self.mp.plotView.addItem(self.mp.centPlot)
        xs, ys = [], []
        for i in data:
            xs.append(i.x())
            ys.append(i.y())
        self.mp.centPlot.setData(xs, ys, size=3, pxMode=False, symbol='+')

    def plotSubaps(self, data):
        self.mp.plotMode = 2
        try:
            self.mp.subapPlot.clear()
        except AttributeError:
            self.mp.subapPlot = pyqtgraph.ScatterPlotItem()
            self.mp.subapPlot.setPen(QtGui.QPen(QtCore.Qt.blue))
            self.mp.subapPlot.setBrush(None)
            self.mp.plotView.addItem(self.mp.subapPlot)
        sizes = []
        xs, ys = [], []
        for i in data:
            sizes.append(i.height())
            xs.append(i.center().x())
            ys.append(i.center().y())
        self.mp.subapPlot.setData(xs, ys, size=sizes, pxMode=False, symbol='s')

    #######OLD STUFF (before dragonAPI)###############
    def getBufferSize(self):
        return self.bufferSizeSlider.value()

    def plotBuffer(self, data):
        buffersize = self.getBufferSize()
        self.ViewBox = self.plotItem.getViewBox()
        self.ViewBox.disableAutoRange()
        self.ViewBox.setRange(xRange=[len(data)-buffersize,len(data)])
        self.plot(data)

    def bufferPlotTest(self):
        data = numpy.array(numpy.random.random(10))
        for i in range(1000):
            data = numpy.append(data, numpy.random.random())
            self.plotBuffer(data)
            pyqtgraph.QtGui.QApplication.processEvents()

            #only keeps buffer, not all data
            # if len(data) > self.getBufferSize():
            #     data = data[-self.getBufferSize():]

    def plotSelectedShape(self):
        index = self.shapeDrawer.index
        data = self.data
        shape = self.shapeDrawer.getShapes().__getitem__(index)
        if type(shape) is QtGui.QGraphicsRectItem:
            cropped_data = self.rectROI.getArrayRegion(data, self.plotItem)
        elif type(shape) is QtGui.QGraphicsLineItem:
            cropped_data = self.lineROI.getArrayRegion(data, self.plotItem)
        self.popout = MagicPlot()
        self.popout.show()
        self.popout.plot(cropped_data)

    def openFits(self):
        fname = unicode(QtGui.QFileDialog.getOpenFileName(self).toUtf8(), encoding="utf-8")
        self.processFits(fits.open(fname)[0].data)

    def processFits(self, data):
        print data.shape

    def saveFits(self):
        data = self.data
        fileDialog = QtGui.QFileDialog()
        fileDialog.setDefaultSuffix("fits")
        fileDialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        if fileDialog.exec_() == QtGui.QFileDialog.Accepted:
            fname = unicode(fileDialog.selectedFiles()[0].toUtf8(), encoding="utf-8")
        try:
            hdu = fits.PrimaryHDU(data)
            hdu.writeto(fname)
            print "current frame written to %s" %fname
        except AttributeError:
            print "no data to save"
        except IOError:
            f = fits.open(fname, mode='update')
            f[0].data = data
            f.flush()
            f.close()
            print "current frame overwritten to %s" %fname

    def updateData(self, raw):
        # print self.data
        # print type(self.data)
        if self.isStreamingData:
            self.data = getData.squareRawPixelData(raw[2][0])
            if self.isPlottingPixels:
                self.plotItem.setImage(self.data)
                self.levels()
                #update data in other window
                try:
                    self.popout
                except AttributeError:
                    pass
                else:
                    if self.popout.isVisible() and self.popout.plotMode == 1:
                        cropped_data = self.lineROI.getArrayRegion(self.data, self.plotItem)
                        self.popout.plotObj.setData(cropped_data)
                        pyqtgraph.QtGui.QApplication.processEvents()
                    elif self.popout.isVisible() and self.popout.plotMode == 2:
                        cropped_data = self.rectROI.getArrayRegion(self.data, self.plotItem)
                        self.popout.plotItem.setImage(cropped_data)
                    else:
                        pass
            return 0
        else:
            return 1

    def plotPixelDataToggle(self, checked):
        if checked:
            self.isPlottingPixels = True
        else:
            self.isPlottingPixels = False

    def startStream(self):
        self.isStreamingData = True
        getData.getData("rtcCalPxlBuf", -1, self.updateData, 10)

    def endStream(self):
        self.isStreamingData = False

    def liveButtonToggle(self, checked):
        if checked:
            self.startStream()
        else:
            self.endStream()

    def subApsToggle(self, checked):
        if checked:
            try:
                self.drawSubAps()
            except AttributeError:
                self.plotMode = 2
                self.drawSubAps()
        else:
            self.shapeDrawer.shapes.clearShapes()

    def drawSubAps(self):
        self.subAps = getData.getSubApRects()
        for i in self.subAps:
            self.shapeDrawer.drawRectFromRect(i)

    def refCentsToggle(self, checked):
        if checked:
            self.isDrawingRefCents = True
            self.refCentPlot = pyqtgraph.ScatterPlotItem()
            self.refCentPlot.setPen(QtGui.QPen(QtCore.Qt.blue))
            self.refCentPlot.setBrush(QtGui.QBrush(QtGui.QColor("blue")))
            self.plotView.addItem(self.refCentPlot)
            try:
                self.getRefCents()
                self.plotRefCents()
            except TypeError:
                print "No ref cents"
        else:
            self.isDrawingRefCents = False
            self.plotView.removeItem(self.refCentPlot)

    def getRefCents(self):
        self.refCents = getData.getRefCentroids()

    def plotRefCents(self):
        index = numpy.arange(len(self.refCents), step=2)
        xs = []
        ys = []
        for i in index:
            xcentre = self.centrePoints[i/2].x()
            ycentre = self.centrePoints[i/2].y()
            xs.append(self.refCents[i] + xcentre)
            ys.append(self.refCents[i+1] + ycentre)
        self.refCentPlot.setData(xs, ys, pxMode=False, size=2, symbol='+')

    def drawArrowsToggle(self, checked):
        if checked:
            self.isDrawingArrows = True
            self.drawArrows()
        else:
            self.isDrawingArrows = False
            self.plotView.removeItem(self.arrowPlotItem)

    def drawArrows(self):
        self.arrowPlotItem = pyqtgraph.ScatterPlotItem()
        self.arrowPlotItem.setPen(QtGui.QPen(QtCore.Qt.red))
        self.arrowPlotItem.setBrush(QtGui.QBrush(QtGui.QColor("red")))
        self.plotView.addItem(self.arrowPlotItem)
        if not self.isStreamingCents:
            self.getCents()

    def updateArrows(self, multiplier=5):
        xs = []
        ys = []
        lengths = []
        arrowList = []
        for i, j in zip(self.plotCents, self.centrePoints):
            line = QtCore.QLineF(i,j)
            angle = line.angle()
            length = multiplier*line.length()
            # lengths.append(line.length())
            # angles.append(line.angle())
            tr = pyqtgraph.QtGui.QTransform()
            tr.rotate(-angle)
            arrow = tr.map(pyqtgraph.makeArrowPath(headLen=0.3, tailLen=0.7, tipAngle=40, tailWidth=0.05))
            arrowList.append(arrow)
            xs.append(i.x() - (multiplier-1)*line.dx())
            ys.append(i.y() - (multiplier-1)*line.dy())
            lengths.append(length)

        self.updateArrowSignal.emit(arrowList, xs, ys, lengths)

    def plotArrows(self, arrowList, xs, ys, lengths):
        self.arrowPlotItem.setData(xs, ys, symbol=arrowList, pxMode=False, size=lengths)

    def plot1dSlopes(self):
        slopes = self.cents
        self.plot(slopes)

class UpdateThread(QtCore.QThread):
    """
    This thread subscribes to RTC. RTC creates another thread which every
    30 frames emits a signal (updateSignal) to update the camera image in the
    GUI. If subscription to RTC fails, this thread emits a signal
    "subscribeFailedSig" to notify the GUI of the problem.
    """
    # Create signals:
    # (a) for updating the plot when new data arrives:
    updateSignal       = QtCore.pyqtSignal( object )
    # (b) for notifying the gui that rtc is not running:
    subscribeFailedSig = QtCore.pyqtSignal()

    def __init__(self, streamNamestr, decimation):
        super(UpdateThread, self).__init__()
        self.streamNamestr = streamNamestr
        self.decimation = decimation
    # This function is called when you say "updateThread.start()":
    def run(self):
        # Subscribe to RTC and ask RTC to display the camera with the arms:
        try:
            self.subscription = DataSubscriber( \
                streamName = self.streamNamestr,              # stream name (as in dragon)
                rtcName    = '',             # darc --prefix
                dummyMode  = False,          # dummy input or real input
                callback   = self.emitUpdateSignal )# callback, i.e. function to
                                          # execute every time new data is ready
        # If subscribing failed,
        except Exception as e:
            # ... notify the main thread:
            self.subscription = None
            self.subscribeFailedSig.emit()
            print e
        else:
            # Activate the subscription, asking for data of every 30-th frame:
            try:
                self.subscription.start( self.decimation )
            # If it doesn't work:
            except Exception as e:
                # Emit signal that subscription failed:
                self.subscription = None
                self.subscribeFailedSig.emit()
                print e

    # This function is called by the RTC everytime new data is ready:
    def emitUpdateSignal(self, data ):
        """
        Emit the signal saying that new data is ready, and pass the data to the
        slot that is connected to this signal.

        Args:
            data : ["data", streamname, (data, frame time, frame number)]
                   this is the structure of a data package coming from darc

        Returns:
            nothing
        """
        # raise Exception # For testing the effect of a broken callback.
        self.updateSignal.emit( data )

    def stopSubscription(self):
        """
        Stop the subscription to the stream for this thread. Doesn't stop the
        updateThread, just the subscription
        """
        self.subscription.stop()


class SubscribeWindow(QtGui.QWidget, subscribeWindow_ui.Ui_subscribeWindow):

    def __init__(self, parent=None):
        super(SubscribeWindow, self).__init__(parent)
        self.setupUi(self)

if __name__ == "__main__":
    app = QtGui.QApplication([])
    w = AOPlot()
    w.show()

    print 'done'
    # sys.exit(app.exec_())
