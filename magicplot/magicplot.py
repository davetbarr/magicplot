import sys
import os
# SRC_PATH = os.path.dirname(os.path.abspath(__file__))
# os.system("pyuic4 {0}/magicPlot.ui > {0}/magicPlot_ui.py".format(SRC_PATH))

import magicPlot_ui
import shapeHolder
import shapeDrawer
import analysisPane_test

from PyQt4 import QtCore, QtGui
import pyqtgraph
import numpy
import warnings
import logging

warnings.filterwarnings('ignore')


# set default colourmaps available
pyqtgraph.graphicsItems.GradientEditorItem.Gradients = pyqtgraph.pgcollections.OrderedDict([
    ('viridis', {'ticks': [(0.,  ( 68,   1,  84, 255)),
                           (0.2, ( 65,  66, 134, 255)),
                           (0.4, ( 42, 118, 142, 255)),
                           (0.6, ( 32, 165, 133, 255)),
                           (0.8, (112, 206,  86, 255)),
                           (1.0, (241, 229,  28, 255))], 'mode':'rgb'}),
    ('grey', {'ticks': [(0.0, (0, 0, 0, 255)),
                        (1.0, (255, 255, 255, 255))], 'mode': 'rgb'}),
        ])


############API STUFF##########

plots = []

def plot(*args, **kwargs):
    """
    Helper function to produce a MagicPlot figure.

    Creates a new window to show data.

    All arguments are passed to MagicPlot.plot()

    Parameters:
        args
        kwargs
    """

    pyqtgraph.mkQApp()
    mplot = MagicPlot()
    item = mplot.plot(*args, **kwargs)
    mplot.show()
    plots.append(mplot)
    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     QtGui.QApplication.instance().exec_()
    return item

class MagicPlot(QtGui.QWidget, magicPlot_ui.Ui_MagicPlot):
    """
    A MagicPlot widget that can be run in a window or embedded.
    """
    dataUpdateSignal1d = QtCore.pyqtSignal(object)
    dataUpdateSignal2d = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(MagicPlot, self).__init__(parent)
        self.windowPlots = []
        self.setupUi(self)
        self.shapeDrawer = shapeDrawer.ShapeDrawer()
        self.drawSplitter.addWidget(self.shapeDrawer)
        self.analysisPane = analysisPane_test.AnalysisPane(parent=self)
        self.analysisSplitter.addWidget(self.analysisPane)
        self.dataUpdateSignal1d.connect(self.analysisPane.updateData)
        self.dataUpdateSignal2d.connect(self.analysisPane.updateData)
        self.dataUpdateSignal1d.connect(self.updatePanBounds)
        self.dataUpdateSignal2d.connect(self.updatePanBounds)

        # Initialise HistogramLUTWidget
        hist = pyqtgraph.HistogramLUTWidget()
        self.histToggle = QtGui.QCheckBox('Auto Levels')
        self.histToggle.setChecked(True)
        self.histToggle.toggled.connect(self.activateHistogram)
        self.hist = hist.item
        histLayout = QtGui.QVBoxLayout()
        histLayout.addWidget(hist)
        histLayout.addWidget(self.histToggle)
        self.histWidget = QtGui.QWidget()
        self.histWidget.setLayout(histLayout)
        self.drawSplitter.insertWidget(0, self.histWidget)

        # need to connect this so its changed by something, at the moment
        # it's just always false
        self.isGettingLevelsFromHist = False

        # Set initial splitter sizes
        self.drawSplitter.setSizes([2,1000,1])
        self.analysisSplitter.setSizes([70,1])
        self.shapeDrawer.hide()
        self.histWidget.hide()
        self.analysisPane.hide()

        # Context menus
        self.showMenu = QtGui.QMenu('Show...')
        showShapes = QtGui.QAction('Shapes', self)
        showShapes.setCheckable(True)
        showShapes.toggled.connect(self.shapeDrawer.setVisible)
        self.showMenu.addAction(showShapes)
        showHist = QtGui.QAction('Histogram', self)
        showHist.setCheckable(True)
        showHist.toggled.connect(self.histWidget.setVisible)
        self.showMenu.addAction(showHist)
        showAnalysis = QtGui.QAction('Analysis', self)
        showAnalysis.setCheckable(True)
        showAnalysis.toggled.connect(self.analysisPane.setVisible)
        self.showMenu.addAction(showAnalysis)

        # Guess that 2-d plot will be common
        # Need to initialise using plotMode = 2 or will not add PlotWidget
        # to layout
        self._plotMode = 2
        self.set2dPlot()
        self.plotMode = 2

        # defualt setting for locking viewBox to data
        self.panBounds = False



 # Methods to setup plot areaD
 ##################################
    def set1dPlot(self):
        print("Set 1d Plot")
        self.deletePlotItem()
        self.plotView = pyqtgraph.PlotWidget()
        # self.plotObj = self.plotView.plotItem.plot()
        # self.plotItem = self.plotView.plotItem
        self.viewBox = self.plotView.getViewBox()
        self.viewBox.menu.addMenu(self.showMenu)

    def set2dPlot(self):
        print("Set 2d Plot")
        self.deletePlotItem()
        self.plotView = pyqtgraph.PlotWidget()
        # self.plotItem = pyqtgraph.ImageItem()
        # self.plotView.addItem(self.plotItem)
        self.viewBox = self.plotView.getViewBox()
        # self.hist.setImageItem(self.plotItem)
        self.viewBox.menu.addMenu(self.showMenu)

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

    @property
    def panBounds(self):
        return self._panBounds

    @panBounds.setter
    def panBounds(self, bounds):
        try:
           self.viewBox.autoRange()
           if bounds is True:
               self._panBounds = True
               rect = self.viewBox.viewRect()
               self.viewBox.setLimits(xMin=rect.left(),
                                       xMax=rect.right(),
                                       yMin=rect.top(),
                                       yMax=rect.bottom())
           else:
               self._panBounds = False
               self.viewBox.setLimits(xMin=None,
                                       xMax=None,
                                       yMin=None,
                                       yMax=None)
        except AttributeError:
           pass

    def updatePanBounds(self):
        if self.panBounds is True:
            self.panBounds = False
            self.panBounds = True

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

    def getImageItem(self):
        """
        Returns an empty MagicPlotImageItem and adds it to magicplot window
        """
        imageItem = MagicPlotImageItem()
        if self.plotMode != 2:
            self.plotMode = 2
        self.plot2d(imageItem)
        return imageItem

    def getDataItem(self):
        """
        Returns an empty MagicPlotDataItem and adds it to magicplot window
        """
        dataItem = MagicPlotDataItem()
        if self.plotMode != 1:
            self.plotMode = 1
        self.plot1d(dataItem)
        return dataItem

    def plot(self, *args, **kwargs):
        """
        Plot data in the MagicPlot window.

        Accepts any dimension array as arguments, and will plot in either 1D or
        2D depending on shape. Accepts data in the following formats:

        ########DATA FORMATS#######

        Parameters:
            args:
            kwargs:

        Returns:
            MagicPlotDataItem: If 1D plot
            MagicPlotImageItem: If 2D plot
        """

        try:
            # Try to plot 1d
            dataItem = MagicPlotDataItem(*args, **kwargs)
            if self.plotMode != 1:
                self.plotMode = 1
            self.plot1d(dataItem)
            self.data = dataItem.getData()
            self.dataUpdateSignal1d.emit(self.data)

        except Exception as e:
            # Try to plot 2d
            if e.message.find('array shape must be') == 0:
                dataItem = MagicPlotImageItem(*args, **kwargs)
                if self.plotMode != 2:
                    self.plotMode = 2
                self.plot2d(dataItem)
                self.data = dataItem.image
                self.dataUpdateSignal2d.emit(self.data)
            else:
                raise

        # lock panning to plot area
        if 'panBounds' in kwargs.keys():
            self.panBounds = kwargs['panBounds']

        self.plotItem = dataItem
        self.plotItem.scene().sigMouseMoved.connect(
                self.mousePosMoved)
        self.shapeDrawer.setView(self.plotView, self.plotItem)
        self.viewBox.autoRange()
        return dataItem



    def plot1d(self, dataItem):
        self.plotView.addItem(dataItem)
        dataItem.sigPlotChanged.connect(lambda:
            self.dataUpdateSignal1d.emit(dataItem.getData()))

    def plot2d(self, imageItem):
        self.plotView.addItem(imageItem)
        imageItem.sigImageChanged.connect(lambda:
            self.dataUpdateSignal2d.emit(imageItem.image))
        self.initHist(imageItem)

    def plotRandom2d(self):
        data = 100*numpy.random.random((100,100))
        self.plot(data)

    def plotRandom1d(self):
        data = 100*numpy.random.random(100)
        self.plot(data)

##########Shape Drawing API######################

    def addRect(self, x, y, width, height, color='r'):
        """
        Add a rectangle to the plot.

        Parameters:
            x (float): x co-ordinate of lower-left corner
            y (float): y co-ordinate of lower-left corner
            width (float): width of rectangle
            height (float): height of rectangle
            color (optional[str]): color of rectangle, see pyqtgraph.mkColor

        Returns:
            QGraphicsRectItem - the rectangle
        """
        qcolor = pyqtgraph.mkColor(color)
        rect = self.shapeDrawer.addRect(x, y, width, height, color=qcolor)
        return rect

    def addLine(self, x1, y1, x2, y2, color='r'):
        """
        Add a line to the plot.

        Parameters:
            x1 (float): x co-ordinate of beginning of line
            y1 (float): y co-ordinate of beginning of line
            x2 (float): x co-ordinate of end of line
            y2 (float): y co-ordinate of end of line
            color (optional[str]): color of line, see pyqtgraph.mkColor

        Returns:
            QGraphicsLineItem - the line
        """
        qcolor = pyqtgraph.mkColor(color)
        line = self.shapeDrawer.addLine(x1, y1, x2, y2, color=qcolor)
        return line

    def addGrid(self, x, y, width, height, rows, columns, color='r'):
        """
        Add a grid to the plot.

        Parameters:
            x (float): x co-ordinate of lower-left corner
            y (float): y co-ordinate of lower-left corner
            width (float): width of grid
            height (float): height of grid
            rows (int): number of rows
            columns (int): number of columns
            color (optional[str]): color of line, see pyqtgraph.mkColor

        Returns:
            Grid
        """
        qcolor = pyqtgraph.mkColor(color)
        grid = self.shapeDrawer.addGrid(x, y, width, height, rows, columns,
            color=qcolor)
        return grid

    def addCircle(self, x, y, r, color='r'):
        """
        Add a circle to the plot.

        Parameters:
            x (float): x co-ordinate of circle center
            y (float): y co-ordinate of circle center
            r (float): radius of circle
            color (optional[str]): color of circle, see pyqtgraph.mkColor

        Returns:
            QGraphicsEllipseItem - the circle
        """
        qcolor = pyqtgraph.mkColor(color)
        circ = self.shapeDrawer.addCirc(x, y, r, color=qcolor)
        return circ

    def initHist(self, imageItem):
        self.hist.setImageItem(imageItem)
        self.hist.sigLevelsChanged.connect(self.histToggle.click)
        levels = imageItem.getLevels()
        try:
            self.hist.setLevels(levels[0], levels[1])
        except TypeError:
            logging.info('Empty ImageItem')

    def activateHistogram(self, checked):
        try:
            if not checked:
                self.hist.sigLevelsChanged.disconnect(self.histToggle.click)
                levels = self.plotItem.getLevels()
                self.plotItem.setOpts(autoLevels=False)
                self.plotItem.sigImageChanged.connect(self.setLevelsFromHist)
                self.hist.setLevels(levels[0], levels[1])
            else:
                self.hist.sigLevelsChanged.connect(self.histToggle.click)
                self.plotItem.setOpts(autoLevels=True)
                im = self.plotItem.image
                self.plotItem.setLevels((im.min(), im.max()))
                self.plotItem.sigImageChanged.disconnect(self.setLevelsFromHist)
        except TypeError:
            pass

    def setLevelsFromHist(self):
        levels = self.hist.getLevels()
        self.plotItem.setLevels(levels)

class MagicPlotImageItem(pyqtgraph.ImageItem):
    """
    A class that defines 2D image data, wrapper around pyqtgraph.ImageItem()

    Returned by MagicPlot.plot()
    """
    def __init__(self, *args, **kwargs):
        super(MagicPlotImageItem, self).__init__(*args, **kwargs)
        self.windows = []
        self.sigImageChanged.connect(self.updateWindows)

    def setData(self, *args, **kwargs):
        """
        Wrapper for pyqtgraph.ImageItem.setImage() to make it consistent with
        pyqtgraph.PlotDataItem.setData()
        """
        self.setImage(*args, **kwargs)

    def plotROI(self, roi):
        window = MagicPlot()
        sliceData = roi.getArrayRegion(self.image, self)
        plt = window.plot(sliceData)
        window.show()
        self.windows.append([window, plt, roi])

    def updateWindows(self):
        for i in self.windows:
            window, plt, roi = i
            sliceData = roi.getArrayRegion(self.image, self)
            plt.setData(sliceData)

class MagicPlotDataItem(pyqtgraph.PlotDataItem):
    """
    A class that defines a set of 1D plot data, wrapper around
    pyqtgraph.PlotDataItem()

    Returned by MagicPlot.plot()
    """
    def __init__(self, *args, **kwargs):
        super(MagicPlotDataItem, self).__init__(*args, **kwargs)
        if 'type' in kwargs.keys():
            self.setType(kwargs['type'])
        if 'color' in kwargs.keys():
            self.setColor(pyqtgraph.mkColor(kwargs['color']))

    def setColor(self, color):
        """
        Set the color of a line plot

        Parameters:
            color (str): The new color of the line,
                        ######POSSIBLE COLORS###########
        """

        self.setPen(pyqtgraph.mkPen(pyqtgraph.mkColor(color)))

    def setType(self, plotType):
        """
        Set the type of plot

        Parameters:
            plotType (str): A string describing the plot type, choose from
                            'scatter' or 'line'
        """

        if plotType == 'scatter':
            self.setPen(None)
            self.setSymbol('o')
        if plotType == 'line':
            self.setColor('w')
            self.setSymbol(None)

if __name__ == "__main__":
    app = QtGui.QApplication([])
    w = MagicPlot()
    w.show()
    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     QtGui.QApplication.instance().exec_()

    try:
        __IPYTHON__
    except NameError:
        __IPYTHON__=False

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        if not __IPYTHON__:
            QtGui.QApplication.instance().exec_()
