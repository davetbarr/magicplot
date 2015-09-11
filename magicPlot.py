import sys
import os
SRC_PATH = os.path.dirname(os.path.abspath(__file__))
os.system("pyuic4 {0}/magicPlot.ui > {0}/magicPlot_ui.py".format(SRC_PATH))

import magicPlot_ui
import shapeHolder
import shapeDrawer
import analysisPane

from PyQt4 import QtCore, QtGui
import pyqtgraph
import numpy

############API STUFF##########

plots = []

def plot(*args, **kwargs):
    pyqtgraph.mkQApp()
    mplot = MagicPlot()
    item = mplot.plot(*args, **kwargs)
    mplot.show()
    plots.append(mplot)
    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     QtGui.QApplication.instance().exec_()
    return item

class MagicPlot(QtGui.QWidget, magicPlot_ui.Ui_MagicPlot):

    dataUpdateSignal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(MagicPlot, self).__init__(parent)
        self.setupUi(self)
        self.shapeDrawer = shapeDrawer.ShapeDrawer()
        self.drawSplitter.addWidget(self.shapeDrawer)
        self.analysisPane = analysisPane.AnalysisPane(parent=self)
        self.analysisSplitter.addWidget(self.analysisPane)
        self.dataUpdateSignal.connect(self.analysisPane.updateData)
        self.dataUpdateSignal.connect(self.analysisPane.region.setData)

        # Initialise HistogramLUTWidget
        self.histWidget = pyqtgraph.HistogramLUTWidget()
        self.hist = self.histWidget.item
        self.drawSplitter.insertWidget(0, self.histWidget)

        # need to connect this so its changed by something, at the moment
        # it's just always false
        self.isGettingLevelsFromHist = False

        # Set initial splitter sizes
        self.drawSplitter.setSizes([0,1,0])
        self.analysisSplitter.setSizes([1,0])

        # Guess that 2-d plot will be common
        # Need to initialise using plotMode = 2 or will not add PlotWidget
        # to layout
        self._plotMode = 2
        self.set2dPlot()
        self.plotMode = 2

        # Initialise ROIs
        self.rectROI = pyqtgraph.RectROI((0,0),(0,0))
        self.lineROI = pyqtgraph.LineSegmentROI((0,0),(0,0))



 # Methods to setup plot areaD
 ##################################
    def set1dPlot(self):
        print("Set 1d Plot")
        self.deletePlotItem()
        self.plotView = pyqtgraph.PlotWidget()
        # self.plotObj = self.plotView.plotItem.plot()
        # self.plotItem = self.plotView.plotItem
        self.viewBox = self.plotView.getViewBox()

    def set2dPlot(self):
        print("Set 2d Plot")
        self.deletePlotItem()
        self.plotView = pyqtgraph.PlotWidget()
        # self.plotItem = pyqtgraph.ImageItem()
        # self.plotView.addItem(self.plotItem)
        self.viewBox = self.plotView.getViewBox()
        # self.hist.setImageItem(self.plotItem)

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
        self.plotLayout.addWidget(self.plotView)

        self.shapeDrawer.clearShapes()

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
        imgPos = pos
        self.mousePos = self.viewBox.mapSceneToView(imgPos)
        value = None

        # Try to index, if not then out of bounds. Don't worry about that.
        # Also ignore if no data plotted
        try:
            if self.plotMode == 1:
                value = self.data[1][self.mousePos.x()]
            if self.plotMode == 2:
                # Only do stuff if position above 0.
                if min(self.mousePos.x(), self.mousePos.y())>0:
                    value = self.data[self.mousePos.x(),self.mousePos.y()]

        except (IndexError, AttributeError):
            pass

        if value!=None:
            self.mousePosLabel.setText ("(%.1f,%.1f) : %.2f"%
                        (self.mousePos.x(), self.mousePos.y(), value) )


    # Plotting methods
    #####################################
    def plot(self, *args, **kwargs):
        try:
            # Try to plot 1d
            dataItem = pyqtgraph.PlotDataItem(*args, **kwargs)
            if self.plotMode != 1:
                self.plotMode = 1
            self.plot1d(dataItem)
            self.data = dataItem.getData()


        except Exception as e:
            # Try to plot 2d
            if e.message.find('array shape must be') == 0:
                dataItem = pyqtgraph.ImageItem(image=args[0])
                if self.plotMode != 2:
                    self.plotMode = 2
                self.plot2d(dataItem)
                self.data = args[0]
            else:
                raise
        self.plotItem = dataItem
        self.plotItem.scene().sigMouseMoved.connect(
                self.mousePosMoved)
        self.shapeDrawer.setView(self.plotView, self.plotItem)
        self.analysisPane.setView(self.plotView, self.plotItem)
        self.dataUpdateSignal.emit(self.data)
        return dataItem

    def plot1d(self, dataItem):
        # self.plotMode = 1
        self.plotView.addItem(dataItem)
        #self.plotView.plotItem.plot(data)
        #self.plotView.autoRange()

    def plot2d(self, imageItem):
        # self.plotMode=2
        # self.plotItem.setImage(data, autoLevels=False)
        # if self.isGettingLevelsFromHist:
        #     self.plotItem.setImage(data, autoLevels=False)
        #     self.plotItem.setLevels(self.hist.getLevels())
        # else:
        #     self.plotItem.setImage(data)
        self.plotView.addItem(imageItem)
        #self.plotView.autoRange()


    def plotRandom2d(self):
        data = 100*numpy.random.random((100,100))
        self.plot(data)

    def plotRandom1d(self):
        data = 100*numpy.random.random(100)
        self.plot(data)

#################################


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
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
