import sys
import os
SRC_PATH = os.path.dirname(os.path.abspath(__file__))
os.system("pyuic4 {0}/magicPlot.ui > {0}/magicPlot_ui.py".format(SRC_PATH))
import magicPlot_ui
import shapeHolder
import shapeDrawer

from PyQt4 import QtCore, QtGui
import pyqtgraph
import numpy
from astropy.io import fits
import getData

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
        self.openFitsFile.clicked.connect(self.openFits)
        self.getLiveData.toggled.connect(self.liveButtonToggle)
        self.maxSlider.valueChanged.connect(self.levels)
        self.minSlider.valueChanged.connect(self.levels)
        self.subApDraw.toggled.connect(self.subApsToggle)
        self.drawCentroids.toggled.connect(self.drawCentroidsToggle)
        self.drawArr.toggled.connect(self.drawArrowsToggle)
        self.drawRefCents.toggled.connect(self.refCentsToggle)


        self.isStreamingData = False
        self.isDrawingCents = False
        self.isDrawingSubAps = False
        self.isDrawingArrows = False
        self.isStreamingCents = False
        self.isDrawingRefCents = False

        # Set initial splitter sizes
        self.drawSplitter.setSizes([200,1])

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

    def updateData(self, raw):
        # print self.data
        # print type(self.data)
        if self.isStreamingData:
            self.data = getData.squareRawPixelData(raw[2][0])
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

    def plotRawPixels(self):
        raw = getData.getData("rtcPxlBuf", 1)["rtcPxlBuf"][0][0]
        data = getData.squareRawPixelData(raw)
        self.plot(data)
        self.data = data

    def plotCalPixels(self):
        raw = getData.getData("rtcCalPxlBuf", 1)["rtcCalPxlBuf"][0][0]
        data = getData.squareRawPixelData(raw)
        self.plot(data)
        self.data = data

    def startStream(self):
        #needs to plot something to initialise
        self.isStreamingData = True
        self.plot(numpy.zeros((2,2)))
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
            self.drawSubAps()
        else:
            self.shapeDrawer.shapes.clearShapes()

    def drawSubAps(self):
        self.subAps = getData.getSubApRects()
        for i in self.subAps:
            self.shapeDrawer.drawRectFromRect(i)

    def drawCentroidsToggle(self, checked):
        if checked:
            self.isDrawingCents = True
            self.drawCents()
        else:
            self.isDrawingCents = False
            self.plotView.removeItem(self.centPlot)

    def drawCents(self):
        self.centPlot = pyqtgraph.ScatterPlotItem(symbol='+')
        self.centPlot.setPen(QtGui.QPen(QtCore.Qt.green))
        self.centPlot.setBrush(QtGui.QBrush(QtGui.QColor("lime")))
        self.plotView.addItem(self.centPlot)
        if not self.isStreamingCents:
            self.getCents()

    def getCents(self):
        self.isStreamingCents = True
        getData.getData("rtcCentBuf", -1, self.updateCents, 10)

    def updateCents(self, raw):
        self.cents = raw[2][0]
        self.centlist = []
        self.centrePoints = []
        index = numpy.arange(len(self.cents), step=2)
        for i in index:
            self.centlist.append(QtCore.QPointF(self.cents[i],self.cents[i+1]))
        for j in self.subAps:
            self.centrePoints.append(j.center())
        self.plotCents = numpy.array(self.centlist)+numpy.array(self.centrePoints)
        # if self.isDrawingArrows:
        #     self.updateArrows()
        # if self.isDrawingCents:
        #     xs = []
        #     ys = []
        #     for i in self.plotCents:
        #         xs.append(i.x())
        #         ys.append(i.y())
        #     self.updateCentSignal.emit(xs, ys)
        # else:
        #     return 1

        if not self.isDrawingArrows and not self.isDrawingCents:
            pass
            #need to implement something to kill the stream (return 1)
        if self.isDrawingArrows:
            self.updateArrows()
        if self.isDrawingCents:
            xs = []
            ys = []
            for i in self.plotCents:
                xs.append(i.x())
                ys.append(i.y())
            self.updateCentSignal.emit(xs, ys)
        return 0

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

    def plotCents(self, xs, ys):
        self.centPlot.setData(xs, ys, pxMode=False, size=2)

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

    def updateArrows(self, multiplier=1):
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

if __name__ == "__main__":
    app = QtGui.QApplication([])
    w = MagicPlot()
    w.show()
    # w.startStream()
    # w.drawSubAps()
    # w.drawCents()

    print 'done'
    sys.exit(app.exec_())
