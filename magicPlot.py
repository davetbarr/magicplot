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

    def __init__(self):
        super(MagicPlot, self).__init__()
        self.setupUi(self)
        self.shapeDrawer = shapeDrawer.ShapeDrawer()
        self.drawSplitter.addWidget(self.shapeDrawer)

        # Guess that 2-d plot will be common
        self._plotMode = 2
        self.set2dPlot()

        # Connect up buttons
        #########################
        # Plot test buttons
        self.plotRand1d.clicked.connect(self.plotRandom1d)
        self.plotRand2d.clicked.connect(self.plotRandom2d)
        self.bufferSizeSlider.valueChanged.connect(self.getBufferSize)
        self.plot1dRealtime.clicked.connect(self.bufferPlotTest)
        self.plotSelected.clicked.connect(self.plotSelectedShape)
        self.openFitsFile.clicked.connect(self.openFits)

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
        self.plotView = pyqtgraph.ImageView()
        self.plotItem = self.plotView.imageItem

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
#        self.plotView.plotItem.plot(data)
        #self.plotView.autoRange()

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
            if len(data) > self.getBufferSize():
                data = data[-self.getBufferSize():]

    def plotSelectedShape(self):
        #nb only takes first item from list at the moment, only works w/ rects
        data = self.data
        rect = self.shapeDrawer.getShapes().__getitem__(0).boundingRect()
        cropped_data = data[int(rect.left()):int(rect.right()),int(rect.top()):int(rect.bottom())]
        newplot = pyqtgraph.ImageView()
        self.drawSplitter.addWidget(newplot)
        newplot.setImage(cropped_data)

    def openFits(self):
        fname = unicode(QtGui.QFileDialog.getOpenFileName(self).toUtf8(), encoding="utf-8")
        self.processFits(fits.open(fname)[0].data)

    def processFits(self, data):
        print data.shape
	
    def plotRawPixels(self):
	raw = getData.getData("dragonrtcPxlBuf", 1) 
	data = getData.processRawPixelData(raw)
        self.plot(data)
        self.data = data

    def plotCalPixels(self):
	raw = getData.getData("dragonrtcCalPxlBuf", 1) 
	data = getData.processRawPixelData(raw)
        self.plot(data)
        self.data = data

if __name__ == "__main__":
    app = QtGui.QApplication([])
    w = MagicPlot()
    w.show()
    w.plotCalPixels()
    print 'done'
    sys.exit(app.exec_())
