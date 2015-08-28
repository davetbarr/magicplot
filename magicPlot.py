import sys
import os
SRC_PATH = os.path.dirname(os.path.abspath(__file__))
os.system("pyuic4 {0}/magicPlot.ui > {0}/magicPlot_ui.py".format(SRC_PATH))
os.system("pyuic4 {0}/subscribeWindow.ui > {0}/subscribeWindow_ui.py".format(SRC_PATH))
import magicPlot_ui
import subscribeWindow_ui
import shapeHolder
import shapeDrawer

from PyQt4 import QtCore, QtGui
import pyqtgraph
import numpy
from astropy.io import fits
import getData
from dragon.rtc import DataSubscriber

class MagicPlot(QtGui.QWidget, magicPlot_ui.Ui_MagicPlot):

    updateCentSignal = QtCore.pyqtSignal(list, list)
    updateArrowSignal = QtCore.pyqtSignal(list, list, list, list)

    def __init__(self, parent=None):
        super(MagicPlot, self).__init__(parent)
        self.setupUi(self)
        self.shapeDrawer = shapeDrawer.ShapeDrawer()
        self.drawSplitter.addWidget(self.shapeDrawer)



        # Guess that 2-d plot will be common
        self._plotMode = 2
        self.set2dPlot()

        # Initialise ROIs
        self.rectROI = pyqtgraph.RectROI((0,0),(0,0))
        self.lineROI = pyqtgraph.LineSegmentROI((0,0),(0,0))

        # Connect signal for change shape
        self.shapeDrawer.changeShapeSignal.connect(self.changeROI)

        self.updateCentSignal.connect(self.plotCents)
        self.updateArrowSignal.connect(self.plotArrows)

        # Connect up buttons
        #########################
        # Plot test buttons
        self.plotRand1d.clicked.connect(self.plotRandom1d)
        self.plotRand2d.clicked.connect(self.plotRandom2d)
        self.bufferSizeSlider.valueChanged.connect(self.getBufferSize)
        self.plot1dRealtime.clicked.connect(self.bufferPlotTest)
        self.plotSelected.clicked.connect(self.plotSelectedShape)
        self.saveFitsFile.clicked.connect(self.saveFits)
        self.getLiveData.toggled.connect(self.liveButtonToggle)
        self.maxSlider.valueChanged.connect(self.levels)
        self.minSlider.valueChanged.connect(self.levels)
        self.subApDraw.toggled.connect(self.subApsToggle)
        #self.drawCentroids.toggled.connect(self.drawCentroidsToggle)
        self.drawArr.toggled.connect(self.drawArrowsToggle)
        self.drawRefCents.toggled.connect(self.refCentsToggle)
        self.but1dSlopes.clicked.connect(self.plot1dSlopes)


        self.isStreamingData = False
        self.isPlottingPixels = False
        self.isPlottingCents = False
        self.isPlottingSubaps = False
        self.isPlottingCalPixels = False
        self.isDrawingArrows = False
        self.isStreamingCents = False
        self.isDrawingRefCents = False


        # Set initial splitter sizes
        self.drawSplitter.setSizes([200,1])

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
            # Haven't done anything to dummyDarc though
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
                self.plotItem.clear()
            except AttributeError:
                pass

    def updateCalPixels(self, data):
        # Find new way of processing raw pixels?
        self.data = getData.squareRawPixelData(data[2][0])
        if self.isPlottingCalPixels and not self.isPlottingPixels:
            self.plotCalPixels(self.data)
        else:
            try:
                self.plotItem.clear()
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
            if self.plotMode == 1:
                self.plot(self.cents)
                return None
            else:
                self.plotCents(self.centCoOrds)
        else:
            try:
                self.centPlot.clear()
            except AttributeError:
                pass

    def updateSubaps(self, data):
        self.subaps = data[2][0].reshape((49,6))  # need to find way of reshaping
        self.subapRects = []                      # maybe get subapLocation
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
                self.subapPlot.clear()
            except AttributeError:
                pass

    def plotPixels(self, data):
        self.plotMode = 2
        self.plotItem.setImage(data)

    def plotCalPixels(self, data):
        self.plotMode = 2
        self.plotItem.setImage(data)

    def plotCents(self, data):
        self.plotMode = 2
        try:
            self.centPlot.clear()
        except AttributeError:
            self.centPlot = pyqtgraph.ScatterPlotItem()
            self.centPlot.setPen(QtGui.QPen(QtCore.Qt.green))
            self.centPlot.setBrush(QtGui.QColor("lime"))
            self.plotView.addItem(self.centPlot)
        xs = []
        ys = []
        for i in data:
            xs.append(i.x())
            ys.append(i.y())
        self.centPlot.setData(xs, ys, size=3, pxMode=False, symbol='+')

    def plotSubaps(self, data):
        self.plotMode = 2
        try:
            self.subapPlot.clear()
        except AttributeError:
            self.subapPlot = pyqtgraph.ScatterPlotItem()
            self.subapPlot.setPen(QtGui.QPen(QtCore.Qt.blue))
            self.subapPlot.setBrush(None)
            self.plotView.addItem(self.subapPlot)
        sizes = []
        xs, ys = [], []
        for i in data:
            sizes.append(i.height())
            xs.append(i.center().x())
            ys.append(i.center().y())
        self.subapPlot.setData(xs, ys, size=sizes, pxMode=False, symbol='s')



 # Methods to setup plot areaD
 ##################################
    def set1dPlot(self):
        print("Set 1d Plot")
        self.deletePlotItem()
        self.plotView = pyqtgraph.PlotWidget()
        self.plotObj = self.plotView.plotItem.plot()
        self.plotItem = self.plotView.plotItem

    def set2dPlot(self):
        print("Set 2d Plot")
        self.deletePlotItem()
        self.plotView = pyqtgraph.PlotWidget()
        self.plotItem = pyqtgraph.ImageItem()
        self.plotView.addItem(self.plotItem)

    @property
    def plotMode(self):
        return self._plotMode

    @plotMode.setter
    def plotMode(self, mode):
        if mode!=self.plotMode:
            if mode==1:
                self.set1dPlot()
            elif mode==2:
                self.set2dPlot()
            else:
                raise ValueError("Plot mode {} not available".format(mode))

        self._plotMode=mode
        # Mouse position printing
        self.plotItem.scene().sigMouseMoved.connect(
                self.mousePosMoved)
        self.plotLayout.addWidget(self.plotView)

        self.shapeDrawer.setView(self.plotView, self.plotItem)

    def deletePlotItem(self):
        for i in reversed(range(self.plotLayout.count())):
            self.plotLayout.itemAt(i).widget().setParent(None)

# Mouse tracking on plot
##############################

    def mousePosMoved(self, pos):
        '''
        method attached to pyqtgraph image widget which gets the mouse position
        If the mouse is in the image, print both the mouse position and
        pixel value to the gui
        '''

        imgPos = self.plotItem.mapFromScene(pos)
        self.mousePos = (imgPos.x(), imgPos.y())
        value = None

        # Try to index, if not then out of bounds. Don't worry about that.
        try:
            if self.plotMode == 1:
                value = self.data[self.mousePos[0]]
            if self.plotMode == 2:
                # Only do stuff if position above 0.
                if min(self.mousePos)>0:
                    value = self.data[self.mousePos[0],self.mousePos[1]]

        except IndexError:
            pass

        if value!=None:
            self.mousePosLabel.setText ("(%.1f,%.1f) : %.2f"%
                        (self.mousePos[0], self.mousePos[1], value) )


    # Plotting methods
    #####################################
    def plot(self, data, dims=None):
        """
        Plot an arbitrary data set.

        Parameters:
            data (ndarray): An array of data, can be 1-d, 2-d or 3-d
            dims (int, optional): The number of dimensions with which to plot each data set.
        """

        print("plot!")
        # If data is to plotted in 1-d
        if dims==1 or data.ndim==1:
            self.plotMode = 1
            self.plot1d(data)

        elif dims==2 or data.ndim==2:
            self.plotMode = 2
            self.plot2d(data)

        else:
            raise ValueError("Can't plot data of this dimension size")
        self.data = data

    def plot1d(self, data):
        self.plotMode = 1
        self.plotObj.setData(data)
        #self.plotView.plotItem.plot(data)
        self.plotView.autoRange()

    def plot2d(self, data):
        self.plotMode=2
        self.plotItem.setImage(data)
        #self.plotView.autoRange()


    def plotRandom2d(self):
        data = numpy.random.random((100,100))
        self.plot(data)
        self.data = data

    def plotRandom1d(self):
        data = numpy.random.random(100)
        self.plot(data)

    # def paintEvent(self, event):
    #     print("Paint Event!")
    #     self.painter = QtGui.QPainter()
    #     self.painter.begin(self)

    #     if len(self.rects):
    #         self.painter.fillRect(
    #                 self.rects[-1].rect(), QtGui.QBrush(QtGui.QColor("red")))

#################################
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

    # def drawCentroidsToggle(self, checked):
    #     if checked:
    #         if not self.isStreamingCents:
    #             self.getCents()
    #         self.isDrawingCents = True
    #         try:
    #             self.drawCents()
    #         except AttributeError:
    #             self.plotMode = 2
    #             self.drawCents()
    #     else:
    #         self.isDrawingCents = False
    #         self.plotView.removeItem(self.centPlot)
    #
    # def drawCents(self):
    #     self.centPlot = pyqtgraph.ScatterPlotItem(symbol='+')
    #     self.centPlot.setPen(QtGui.QPen(QtCore.Qt.green))
    #     self.centPlot.setBrush(QtGui.QBrush(QtGui.QColor("lime")))
    #     self.plotView.addItem(self.centPlot)
    #     if not self.isStreamingCents:
    #         self.getCents()
    #
    # def getCents(self):
    #     self.isStreamingCents = True
    #     getData.getData("rtcCentBuf", -1, self.updateCents, 10)

    # def updateCents(self, raw):
    #     self.cents = raw[2][0]
    #     self.centlist = []
    #     self.centrePoints = []
    #     index = numpy.arange(len(self.cents), step=2)
    #     for i in index:
    #         self.centlist.append(QtCore.QPointF(self.cents[i],self.cents[i+1]))
    #     for j in self.subAps:
    #         self.centrePoints.append(j.center())
    #     self.plotCents = numpy.array(self.centlist)+numpy.array(self.centrePoints)
    #
    #     if not self.isDrawingArrows and not self.isDrawingCents:
    #         pass
    #         #need to implement something to kill the stream (return 1)
    #     if self.isDrawingArrows:
    #         self.updateArrows()
    #     if self.isDrawingCents:
    #         xs = []
    #         ys = []
    #         for i in self.plotCents:
    #             xs.append(i.x())
    #             ys.append(i.y())
    #         self.updateCentSignal.emit(xs, ys)
    #     return 0

    # def generateImage(self):
    #     fShape = []
    #     # fShape.append(self.subAps[0])
    #     # fShape.append(self.subAps[4])
    #     # fShape.append(self.subAps[10])
    #     # fShape.append(self.subAps[11])
    #     # fShape.append(self.subAps[17])
    #     # fShape.append(self.subAps[23])
    #     # fShape.append(self.subAps[24])
    #     # fShape.append(self.subAps[25])
    #
    #     fShapes = [0,4,10,11,17,23,24,25]
    #     centres = []
    #     for i in self.subAps:
    #         print i
    #         centres.append(i.center())
    #
    #     print centres
    #
    #     frame1 = numpy.zeros((128,128), dtype=numpy.int16)
    #
    #     for j in range(len(centres)):
    #         if j in fShapes:
    #             rand = int(5*numpy.random.random())
    #             x = centres[j].x()
    #             y = centres[j].y()
    #             frame1[x+rand:x+rand+2,y-rand:y-rand+2] = 100
    #         else:
    #             x = centres[j].x()
    #             y = centres[j].y()
    #             frame1[x,y] = 100
    #
    #     frame2 = numpy.roll(frame1,1)
    #     frame3 = numpy.roll(frame2,1)
    #
    #     output = numpy.array([frame1, frame2, frame3])
    #     pyqtgraph.image(output)
    #     hdu = fits.PrimaryHDU(output)
    #     hdu.writeto('test.fits')

    # def plotCents(self, data):
    #     print "plotCents"
    #     #self.centPlot.setData(xs, ys, pxMode=False, size=2)

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

    def changeROI(self):
        index = self.shapeDrawer.index
        shape = self.shapeDrawer.getShapes().__getitem__(index)

        #this gives ?warnings? when the ROI doesn't exist yet, but doesn't crash
        self.plotView.removeItem(self.rectROI)
        self.plotView.removeItem(self.lineROI)
        ##########

        if type(shape) is QtGui.QGraphicsRectItem:
            rect = shape.boundingRect()
            newPoint = QtCore.QPointF((rect.left()), rect.top())
            self.rectROI.setPos(newPoint)
            self.rectROI.setSize([rect.width(), rect.height()])
            self.plotView.addItem(self.rectROI)
        elif type(shape) is QtGui.QGraphicsLineItem:
            line = shape.line()
            p1, p2 = line.p1(), line.p2()
            h1, h2 = self.lineROI.getHandles()
            h1.setPos(p1)
            h2.setPos(p2)
            self.plotView.addItem(self.lineROI)
        else:
            print "Not a valid shape"

    def levels(self):
        maxval = self.maxSlider.value()
        minval = self.minSlider.value()
        self.plotItem.setLevels([minval,maxval])

    def colorMapToggle(self, checked):
        if checked:
            self.colorMap()
        else:
            self.plotItem.setLookupTable()

    def colorMap(self):
        pos = numpy.array([0,0.49,0.5,1])
        color = numpy.array([[0,0,0,255], [255,255,255,255], [255,255,0,255], [255,0,0,255]], dtype=numpy.ubyte)
        colorMap = pyqtgraph.ColorMap(pos, color)
        lut = colorMap.getLookupTable(0.0, 1.0, 256)
        self.plotItem.setLookupTable(lut)

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
    w = MagicPlot()
    w.show()

    print 'done'
    sys.exit(app.exec_())
