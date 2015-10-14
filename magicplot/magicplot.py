import sys
import os
# SRC_PATH = os.path.dirname(os.path.abspath(__file__))
# os.system("pyuic4 {0}/magicPlot.ui > {0}/magicPlot_ui.py".format(SRC_PATH))

# Try importing PyQt5, if not fall back to PyQt4
try:
    from PyQt5 import QtCore, QtGui, QtWidgets, uic
    PYQTv = 5
except (ImportError, RuntimeError):
    from PyQt4 import QtCore, QtGui, uic
    QtWidgets = QtGui
    PyQTv = 4

PATH = os.path.dirname(os.path.abspath(__file__))
Ui_MagicPlot= uic.loadUiType(os.path.join(PATH,"magicPlot.ui"))[0]
# import magicPlot_ui
import shapeHolder
import shapeDrawer
import analysisPane
import transforms

import pyqtgraph
import numpy
import logging



# set default colourmaps available
pyqtgraph.graphicsItems.GradientEditorItem.Gradients = pyqtgraph.pgcollections.OrderedDict([
    ('viridis', {'ticks': [(0.,  ( 68,   1,  84, 255)),
                           (0.2, ( 65,  66, 134, 255)),
                           (0.4, ( 42, 118, 142, 255)),
                           (0.6, ( 32, 165, 133, 255)),
                           (0.8, (112, 206,  86, 255)),
                           (1.0, (241, 229,  28, 255))], 'mode':'rgb'}),
    ('coolwarm', {'ticks': [(0.0, ( 59,  76, 192)),
                            (0.5, (220, 220, 220)),
                            (1.0, (180, 4, 38))], 'mode': 'rgb'}),
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

class MagicPlot(QtWidgets.QWidget, Ui_MagicPlot):
    """
    A MagicPlot widget that can be run in a window or embedded.

    Parameters:
        parent (Optional[QObject])

    Attributes:
        plotMode (int): 1 = 1D plot, 2 = 2D plot

        windowPlots (list): List of additional pop-up window plots created
            by plotting Regions of Interest

        plotItems (list): List of plotItems (MagicPlotDataItem) that are 
            currently plotted in the window. Note: only 1 MagicPlotImageItem
            can exist at a time

        shapeDrawer (shapeDrawer.ShapeDrawer): controls drawing of shapes on the
            plot 

        analysisPane (analysisPane.AnalysisPane): controls data analysis plugins 

        transformer (transforms.Transformer): controls the application of
            transform plugins to the data

        histWidget (QWidget): QWidget containing histogram for image data, boxes
            for manually setting histogram and Auto-Levels checkbox

        hist (pyqtgraph.HistogramLUTItem): pyqtgraph histogram item

        showMenu (QMenu): context menu for showing histogram, analysis and
            shapes

        panBounds (bool): If True, locks the panning of the plot to the data.
            True by default.

    """
    dataUpdateSignal1d = QtCore.pyqtSignal(object)
    dataUpdateSignal2d = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(MagicPlot, self).__init__(parent)
        self.windowPlots = []
        self.setupUi(self)
        self.shapeDrawer = shapeDrawer.ShapeDrawer()
        self.drawSplitter.addWidget(self.shapeDrawer)
        self.analysisPane = analysisPane.AnalysisPane(parent=self)
        self.analysisSplitter.addWidget(self.analysisPane)
        self.transformer = transforms.Transformer()
        self.dataUpdateSignal1d.connect(self.dataUpdateHandler)
        self.dataUpdateSignal2d.connect(self.dataUpdateHandler)
 
        self.setWindowTitle("Magic Plot") 

        # Initialise HistogramLUTWidget
        self.histWidget = QtWidgets.QWidget()
        hist = pyqtgraph.HistogramLUTWidget()
        self.histWidget.maxLevelBox = QtWidgets.QDoubleSpinBox()
        self.histWidget.maxLevelBox.valueChanged.connect(self.setHistFromBoxes)
        self.histWidget.minLevelBox = QtWidgets.QDoubleSpinBox()
        self.histWidget.minLevelBox.valueChanged.connect(self.setHistFromBoxes)
        self.histWidget.maxLevelBox.setRange(-10000,10000)
        self.histWidget.minLevelBox.setRange(-10000,10000)
        self.histWidget.histToggle = QtWidgets.QCheckBox('Auto Levels')
        self.histWidget.histToggle.setChecked(True)
        self.histWidget.histToggle.toggled.connect(self.activateHistogram)
        self.hist = hist.item
        boxLayout = QtWidgets.QGridLayout()
        boxLayout.addWidget(QtWidgets.QLabel('Max'), 0, 0)
        boxLayout.addWidget(self.histWidget.maxLevelBox, 0, 1)
        boxLayout.addWidget(QtWidgets.QLabel('Min'), 1, 0)
        boxLayout.addWidget(self.histWidget.minLevelBox, 1, 1)
        histLayout = QtWidgets.QVBoxLayout()
        histLayout.addWidget(hist)
        histLayout.addLayout(boxLayout)
        histLayout.addWidget(self.histWidget.histToggle)
        self.histWidget.setLayout(histLayout)
        self.drawSplitter.insertWidget(0, self.histWidget)

        # Set initial splitter sizes, hide by default
        self.drawSplitter.setSizes([2,1000,1])
        self.analysisSplitter.setSizes([70,1])
        self.shapeDrawer.hide()
        self.histWidget.hide()
        self.analysisPane.hide()

        # Context menu for showing panes
        self.showMenu = QtWidgets.QMenu('Show...')
        showShapes = QtWidgets.QAction('Shapes', self)
        showShapes.setCheckable(True)
        showShapes.toggled.connect(self.shapeDrawer.setVisible)
        self.showMenu.addAction(showShapes)
        showHist = QtWidgets.QAction('Histogram', self)
        showHist.setCheckable(True)
        showHist.toggled.connect(self.histWidget.setVisible)
        self.showMenu.addAction(showHist)
        showAnalysis = QtWidgets.QAction('Analysis', self)
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
        self.panBounds = True

        # default setting for autoLevels of 2d plots
        self.autoLevels = True



 # Methods to setup plot areaD
 ##################################
    def set1dPlot(self):
        logging.debug("Set 1d Plot")
        self.deletePlotItem()
        self.plotView = pyqtgraph.PlotWidget()
        # self.plotObj = self.plotView.plotItem.plot()
        # self.plotItem = self.plotView.plotItem
        self.viewBox = self.plotView.getViewBox()
        self.viewBox.menu.addMenu(self.showMenu)
        self.viewBox.menu.addMenu(self.transformer.transMenu)
        self.analysisPane.initRegion(self.plotView)
        self.plotItems = []

    def set2dPlot(self):
        logging.debug("Set 2d Plot")
        self.deletePlotItem()
        self.plotView = pyqtgraph.PlotWidget()
        # self.plotItem = pyqtgraph.ImageItem()
        # self.plotView.addItem(self.plotItem)
        self.viewBox = self.plotView.getViewBox()
        # self.hist.setImageItem(self.plotItem)
        self.viewBox.menu.addMenu(self.showMenu)
        self.viewBox.menu.addMenu(self.transformer.transMenu)
        self.plotItems = []

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
        """
        Sets panBounds by autoRanging the viewBox then setting limits
        """
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
        """
        method attached to pyqtgraph image widget which gets the mouse position
        If the mouse is in the image, print both the mouse position and
        pixel value to the gui
        """
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

        Returns:
            MagicPlotImageItem: an empty MagicPlotImageItem
        """
        imageItem = MagicPlotImageItem(self)
        if self.plotMode != 2:
            self.plotMode = 2
        self.plot2d(imageItem)
        return imageItem

    def getDataItem(self):
        """
        Returns an empty MagicPlotDataItem and adds it to magicplot window

        Returns:
            MagicPlotDataItem: an empty MagicPlotDataItem
        """
        dataItem = MagicPlotDataItem(self)
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
            dataItem = MagicPlotDataItem(self, *args, **kwargs)
            if self.plotMode != 1:
                self.plotMode = 1
            self.plot1d(dataItem)
            self.data = dataItem.getData()
            self.dataUpdateSignal1d.emit(self.data)

        except Exception as e:
            # Try to plot 2d
            if e.message.find('array shape must be') == 0:
                dataItem = MagicPlotImageItem(self, *args, **kwargs)
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

        if self.panBounds:
            self.updatePanBounds()

        # add the plotItem to the list
        self.plotItems.append(dataItem)
        self.transformer.sigActiveToggle.connect(
                dataItem.transformToggle)
        return dataItem


    def plot1d(self, dataItem):
        """
        Add a MagicPlotDataItem to the 1D plot.

        Parameters:
            dataItem (MagicPlotDataItem): data item containing data to plot,
                returned by MagicPlot.plot() or MagicPlot.getDataItem()
        """
        self.plotView.addItem(dataItem)
        dataItem.sigPlotChanged.connect(lambda:
            self.dataUpdateSignal1d.emit(dataItem.getData()))
        self.plotItem = dataItem
        self.plotItem.scene().sigMouseMoved.connect(
                self.mousePosMoved)
        self.shapeDrawer.setView(self.plotView, self.plotItem)
        self.viewBox.autoRange()

    def plot2d(self, imageItem):
        """
        Add a MagicPlotImageItem to the 2D plot.

        Only 1 ImageItem can be added at a time, so this overwrites whatever
        is already plotted.

        Parameters:
            imageItem (MagicPlotImageItem): image item containing data to plot,
                returned by MagicPlot.plot() or MagicPlot.getImageItem()
        """
        self.plotView.addItem(imageItem)
        imageItem.sigImageChanged.connect(lambda:
            self.dataUpdateSignal2d.emit(imageItem.image))
        self.plotItem = imageItem
        self.initHist(imageItem)
        self.plotItem.scene().sigMouseMoved.connect(
                self.mousePosMoved)
        self.shapeDrawer.setView(self.plotView, self.plotItem)

    def updatePlot(self):
        """
        Wrapper around QApplication.processEvents() so that live plotting works
        """
        QtGui.QApplication.instance().processEvents()


    def dataUpdateHandler(self, data):
        """
        Connected to the dataUpdate1d and dataUpdate2d signals, handles
        updating data in the plot.
        """
        self.analysisPane.updateData(data)
        if self.plotMode == 2 and self.autoLevels:
            self.setHistFromData(data)

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
            color (Optional[str]): color of rectangle, see pyqtgraph.mkColor

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
            color (Optional[str]): color of line, see pyqtgraph.mkColor

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
            color (Optional[str]): color of line, see pyqtgraph.mkColor

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
            color (Optional[str]): color of circle, see pyqtgraph.mkColor

        Returns:
            QGraphicsEllipseItem - the circle
        """
        qcolor = pyqtgraph.mkColor(color)
        circ = self.shapeDrawer.addCirc(x, y, r, color=qcolor)
        return circ
    
    def addElipse(self, x, y, rx, ry, color="r"):
        """
        Add an elipse to the plot.

        Parameters:
            x (float): x co-ordinate of elipse center
            y (float): y co-ordinate of elipse center
            rx (float): radius of elipse in x direction
            ry (float): radius of elipse in y direction
            color (Optional[str]): color of circle, see pyqtgraph.mkColor

        Returns:
            QGraphicsEllipseItem - the circle
        """
        qcolor = pyqtgraph.mkColor(color)
        elipse = self.shapeDrawer.addElipse(x, y, rx, ry, color=qcolor)
        return elipse

############ Histogram ###############

    def initHist(self, imageItem):
        """
        Initialise the histogram to control the levels of 2D plots.

        Parameters:
            imageItem (MagicPlotImageItem): the image item connected to
                the histogram
        """
        self.hist.setImageItem(imageItem)
        self.hist.sigLevelsChanged.connect(self.histWidget.histToggle.click)
        levels = imageItem.getLevels()
        try:
            self.hist.setLevels(levels[0], levels[1])
            self.histWidget.maxLevelBox.setValue(levels[1])
            self.histWidget.minLevelBox.setValue(levels[0])
            self.histWidget.histToggle.setChecked(True)
        except TypeError:
            logging.info('Empty ImageItem')

    def activateHistogram(self, checked):
        """
        Handles the "AutoLevels" checkbox below the histogram.

        When unchecked, the histogram will control the levels of the image,
        when checked image will use autoLevels=True

        Parameters:
            checked (bool): True if checkbox is checked, otherwise false
        """
        self.autoLevels = checked
        try:
            if not checked:
                self.hist.sigLevelsChanged.disconnect(
                    self.histWidget.histToggle.click)
                levels = self.plotItem.getLevels()
                self.plotItem.setOpts(autoLevels=False)
                self.plotItem.sigImageChanged.connect(self.setLevelsFromHist)
                self.hist.sigLevelsChanged.connect(self.setLevelBoxes)
                self.hist.setLevels(levels[0], levels[1])
            else:
                self.plotItem.setOpts(autoLevels=True)
                im = self.plotItem.image
                self.plotItem.setLevels((im.min(), im.max()))
                self.plotItem.sigImageChanged.disconnect(self.setLevelsFromHist)
                self.hist.setLevels(im.min(), im.max())
                self.hist.sigLevelsChanged.connect(
                    self.histWidget.histToggle.click)
        except TypeError:
            raise

    def setLevelBoxes(self):
        """
        Set the "Max" and "Min" boxes below the histogram to the levels
        that the histogram is set to.
        """
        levels = self.hist.getLevels()
        self.histWidget.maxLevelBox.setValue(levels[1])
        self.histWidget.minLevelBox.setValue(levels[0])

    def setHistFromBoxes(self):
        """
        Set the histogram levels from the "Max" and "Min" boxes
        """
        _max, _min = self.histWidget.maxLevelBox.value(), \
            self.histWidget.minLevelBox.value()
        self.hist.setLevels(_min, _max)

    def setLevelsFromHist(self):
        """
        Set the levels of the image from the histogram
        """
        levels = self.hist.getLevels()
        self.plotItem.setLevels(levels)

    def setHistFromData(self, data):
        """
        Set the levels of histogram from arbitrary data, fixes
        bug where updating data was not updating histogram

        Parameters:
            data (numpy.ndarray)
        """
        self.hist.blockSignals(True)
        _min, _max = data.min(), data.max()
        self.hist.setLevels(_min, _max)
        self.setLevelBoxes()
        self.hist.blockSignals(False)

class MagicPlotImageItem(pyqtgraph.ImageItem):
    """
    A class that defines 2D image data, wrapper around pyqtgraph.ImageItem()

    Returned by MagicPlot.plot()

    Use MagicPlot.getImageItem() to get an empty MagicPlotImageItem to use

    Parameters:
        parent (QObject): when plotting using MagicPlot.plot() or
            MagicPlot.getImageItem() this is set to the MagicPlot window
            so that transforms can be applied to the data
    
    Attributes:
        parent (QObject): the parent object of this ImageItem

        windows (list): List of pop-up MagicPlot windows generated
            by plotROI, used to update these plots and keep them in scope

        originalData (numpy.ndarray): When transforms are applied, the
            pre-transformed data is kept and replotted if the tranforms
            are turned off
    """
    def __init__(self, parent,  *args, **kwargs):
        self.parent = parent
        super(MagicPlotImageItem, self).__init__(*args, **kwargs)
        self.windows = []
        self.sigImageChanged.connect(self.updateWindows)
        self.originalData = None

    def setData(self, data, **kwargs):
        """
        Wrapper for pyqtgraph.ImageItem.setImage() to make it consistent with
        pyqtgraph.PlotDataItem.setData()
        """
        self.setImage(image=data, **kwargs)
    
    def setImage(self, image=None, **kargs):
        """
        Extension of pyqtgraph.ImageItem.setImage() to allow transforms to be
        applied to the data before it is plotted.
        """
        # transform if transformer is active
        if self.parent.transformer.active and image is not None:
            image = self.parent.transformer.transform(image)

        # call the pyqtgraph.ImageItem.setImage() function    
        super(MagicPlotImageItem, self).setImage(image, **kargs)

    def informViewBoundsChanged(self):
        super(MagicPlotImageItem, self).informViewBoundsChanged()
        if self.parent.panBounds:
            self.parent.updatePanBounds()

    def getData(self):
        """
        Wrapper around pyqtgraph.ImageItem.image to make it consistent with
        pyqtgraph.PlotDataItem.getData()
        """
        return self.image

    def plotROI(self, roi):
        """
        Plot the current region of interest in a new MagicPlot window.

        Parameters:
            roi (pyqtgraph.ROI): Region of Interest to use for plotting
        """
        window = MagicPlot()
        sliceData = roi.getArrayRegion(self.image, self)
        plt = window.plot(sliceData)
        window.show()
        self.windows.append([window, plt, roi])

    def updateWindows(self):
        """
        Update the RoI plots
        """
        for i in self.windows:
            try:
                window, plt, roi = i
                sliceData = roi.getArrayRegion(self.image, self)
                plt.setData(sliceData)
            except:
                logging.debug("RoI doesn't exist, removing window from list")
                self.windows.remove(i)

    def transformToggle(self, checked):
        """
        Handles clicks on the 'Activate Transforms' menu option when this
        ImageItem is plotted. Stores the untransformed data.

        Parameters:
            checked (bool): If True, then transforms are applied and the
                original data is saved.
        """
        if checked:
            self.originalData = self.getData()
            self.setData(self.getData())
        else:
            self.setData(self.originalData)
            self.originalData = None

    def updatePlot(self):
        """
        Wrapper around QApplication.processEvents() so that live plotting works
        """
        QtGui.QApplication.instance().processEvents()


class MagicPlotDataItem(pyqtgraph.PlotDataItem):
    """
    A class that defines a set of 1D plot data, wrapper around
    pyqtgraph.PlotDataItem()

    Returned by MagicPlot.plot()

    Use MagicPlot.getDataItem() to generate an empty MagicPlotDataItem
    to use

    Parameters:
        parent (QObject): when plotting using MagicPlot.plot() or
            MagicPlot.getDataItem() this is set to the MagicPlot window
            so that transforms can be applied to the data

    Attributes:
        parent (QObject): the parent object of this DataItem

        originalData (numpy.ndarray): When transforms are applied, the
        data = args[0]
        # transform if transformer is active
        if self.parent.transformer.active and data is not None:
            data = self.parent.transformer.transform(data)
            super(MagicPlotDataItem, self).setData(data, **kargs)
            return
    """
    def __init__(self, *args, **kargs):
        # setData with pyqtgraph.PlotDataItem.setData()
        super(MagicPlotDataItem, self).setData(*args, **kargs)

    def informViewBoundsChanged(self):
        super(MagicPlotDataItem, self).informViewBoundsChanged()
        if self.parent.panBounds:
            self.parent.updatePanBounds()

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

    def transformToggle(self, checked):
        """
        Handles clicks on the 'Activate Transforms' menu option when this
        DataItem is plotted. Stores the untransformed data.

        Parameters:
            checked (bool): If True, then transforms are applied and the
                original data is saved.
        """
        if checked:
            self.originalData = self.getData()
            self.setData(self.getData())
        else:
            self.setData(self.originalData)
            self.originalData = None

    def updatePlot(self):
        """
        Wrapper around QApplication.processEvents() so that live plotting works
        """
        QtGui.QApplication.instance().processEvents()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    w = MagicPlot()
    w.show()
    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     QtWidgets.QApplication.instance().exec_()

    try:
        __IPYTHON__
    except NameError:
        __IPYTHON__=False

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        if not __IPYTHON__:
            QtWidgets.QApplication.instance().exec_()
