import os
# SRC_PATH = os.path.dirname(os.path.abspath(__file__))
# os.system("pyuic4 {0}/magicPlot.ui > {0}/magicPlot_ui.py".format(SRC_PATH))

# Try importing PyQt5, if not fall back to PyQt4
try:
    from PyQt5 import QtCore, QtGui, QtWidgets, uic
    from PyQt5.QtWidgets import QMenu, QAction, QMenuBar
    PYQTv = 5
except (ImportError, RuntimeError):
    from PyQt4 import QtCore, QtGui, uic
    QtWidgets = QtGui
    PyQTv = 4

from matplotlib import cm
import matplotlib.pyplot as plt

PATH = os.path.dirname(os.path.abspath(__file__))
Ui_MagicPlot= uic.loadUiType(os.path.join(PATH,"magicPlot.ui"))[0]
# import magicPlot_ui
from . import shapeHolder, shapeDrawer, analysisPane, transforms, plugins

# from . import pyqtgraph
import pyqtgraph
import numpy
import logging

# set default colourmaps available
# pyqtgraph.graphicsItems.GradientEditorItem.Gradients = pyqtgraph.pgcollections.OrderedDict([
#     ('viridis', {'ticks': [(0.,  ( 68,   1,  84, 255)),
#                            (0.2, ( 65,  66, 134, 255)),
#                            (0.4, ( 42, 118, 142, 255)),
#                            (0.6, ( 32, 165, 133, 255)),
#                            (0.8, (112, 206,  86, 255)),
#                            (1.0, (241, 229,  28, 255))], 'mode':'rgb'}),
#     ('coolwarm', {'ticks': [(0.0, ( 59,  76, 192)),
#                             (0.5, (220, 220, 220)),
#                             (1.0, (180, 4, 38))], 'mode': 'rgb'}),
#     ('grey', {'ticks': [(0.0, (0, 0, 0, 255)),
#                         (1.0, (255, 255, 255, 255))], 'mode': 'rgb'}),
#         ])




############API STUFF##########

def plot(*args, **kwargs):
    """
    Helper function to produce a MagicPlot figure.

    Creates a new window to show data.

    All arguments are passed to MagicPlot.plot()

    Parameters:
        args
        kwargs

    Returns:
        MagicPlot window object
    """

    pyqtgraph.mkQApp()
    mplot = MagicPlot()
    item = mplot.plot(*args, **kwargs)
    mplot.show()
    # plots.append(mplot)
    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     QtGui.QApplication.instance().exec_()
    return mplot

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

        # Create exportMenuAction before it's used in set2dPlot
        self.exportMenu = QtWidgets.QMenu('Export')
        self.exportMenuAction = QtWidgets.QAction('Export', self)
        self.exportMenuAction.setMenu(self.exportMenu)

        # Create toggleFullscreenAction before it's used in set2dPlot
        self.toggleFullscreenAction = QtWidgets.QAction('Fullscreen Mode', self)
        self.toggleFullscreenAction.setCheckable(True)
        self.toggleFullscreenAction.toggled.connect(self.toggleFullscreen)

        # Initialize transformer before setting the plot mode
        self.transformer = transforms.Transformer()

        # Initialize the showMenu
        self.showMenu = QtWidgets.QMenu('Show...', self)
        showShapes = QtWidgets.QAction('Shapes', self)
        showShapes.triggered.connect(lambda: self.shapeSplitter.setSizes([1000, 1]))
        self.showMenu.addAction(showShapes)
        showHist = QtWidgets.QAction('Histogram', self)
        showHist.triggered.connect(lambda: self.histSplitter.setSizes([1, 1000]))
        self.showMenu.addAction(showHist)
        showAnalysis = QtWidgets.QAction('Analysis', self)
        showAnalysis.triggered.connect(lambda: self.analysisSplitter.setSizes([1000, 1]))
        self.showMenu.addAction(showAnalysis)

        # Initialize the viewBox by setting a default plot mode
        self._plotMode = 2  # Default to 2D plot mode
        self.set2dPlot()

        # Add a menu bar to the MagicPlot window
        self.menuBar = QMenuBar(self)
        self.gridLayout.setMenuBar(self.menuBar)

        self.shapeDrawer = shapeDrawer.ShapeDrawer()
        self.shapeLayout.addWidget(self.shapeDrawer)
        self.analysisPane = analysisPane.AnalysisPane(parent=self)
        self.analysisLayout.addWidget(self.analysisPane)
        # Transformer already initialized above
        self.dataUpdateSignal1d.connect(self.dataUpdateHandler)
        self.dataUpdateSignal2d.connect(self.dataUpdateHandler)

        self.setWindowTitle("MagicPlot")

        # Add export functionality
        self.setupExportMenu()
        
        # Add keyboard shortcuts
        self.setupShortcuts()

        # Add color map menu
        self.setupColorMapMenu()

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
        self.histLayout.insertWidget(0, self.histWidget)

        # Set initial splitter sizes, hide by default
        self.shapeSplitter.setSizes([1,0])
        self.analysisSplitter.setSizes([1,0])
        self.histSplitter.setSizes([0,1])

        # Initialize the showMenu attribute
        self.showMenu = QtWidgets.QMenu('Show...', self)
        showShapes = QtWidgets.QAction('Shapes', self)
        showShapes.triggered.connect(lambda: self.shapeSplitter.setSizes([1000, 1]))
        self.showMenu.addAction(showShapes)
        showHist = QtWidgets.QAction('Histogram', self)
        showHist.triggered.connect(lambda: self.histSplitter.setSizes([1, 1000]))
        self.showMenu.addAction(showHist)
        showAnalysis = QtWidgets.QAction('Analysis', self)
        showAnalysis.triggered.connect(lambda: self.analysisSplitter.setSizes([1000, 1]))
        self.showMenu.addAction(showAnalysis)

        # Create a custom context menu for the viewBox
        # ViewBox doesn't have setMenu, we need to access the existing menu
        self.viewBoxMenu = self.viewBox.menu

        # Add the showMenu to the custom context menu
        self.viewBoxMenu.addMenu(self.showMenu)

        self.plotItems = []

        # Menu action for toggling fullscreen mode
        self.toggleFullscreenAction = QtWidgets.QAction('Fullscreen Mode', self)
        self.toggleFullscreenAction.setCheckable(True)
        self.toggleFullscreenAction.toggled.connect(self.toggleFullscreen)

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

    def mkQApp(self):
        return pyqtgraph.mkQApp()

    def setupExportMenu(self):
        """
        Sets up the export menu with options to export data and plots in various formats.
        """
        # Create export menu
        self.exportMenu = QtWidgets.QMenu('Export')
        
        # Export image options
        exportImageAction = QtWidgets.QAction('Export Plot as Image...', self)
        exportImageAction.triggered.connect(self.exportPlotAsImage)
        self.exportMenu.addAction(exportImageAction)
        
        # Export data options
        exportDataAction = QtWidgets.QAction('Export Data...', self)
        exportDataAction.triggered.connect(self.exportData)
        self.exportMenu.addAction(exportDataAction)
        
        # Export figure settings
        exportSettingsAction = QtWidgets.QAction('Export Figure Settings...', self)
        exportSettingsAction.triggered.connect(self.exportFigureSettings)
        self.exportMenu.addAction(exportSettingsAction)
        
        # Import figure settings
        importSettingsAction = QtWidgets.QAction('Import Figure Settings...', self)
        importSettingsAction.triggered.connect(self.importFigureSettings)
        self.exportMenu.addAction(importSettingsAction)
        
        # Session management
        self.exportMenu.addSeparator()
        saveSessionAction = QtWidgets.QAction('Save Session...', self)
        saveSessionAction.triggered.connect(self.saveSession)
        self.exportMenu.addAction(saveSessionAction)
        
        loadSessionAction = QtWidgets.QAction('Load Session...', self)
        loadSessionAction.triggered.connect(self.loadSession)
        self.exportMenu.addAction(loadSessionAction)
        
        # Add to viewBox menu
        # This makes the export menu accessible from the plot context menu
        self.exportMenuAction = QtWidgets.QAction('Export', self)
        self.exportMenuAction.setMenu(self.exportMenu)

    def setupShortcuts(self):
        """
        Set up keyboard shortcuts for common actions in MagicPlot.
        """
        # Fullscreen shortcut (F11)
        self.fullscreenShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("F11"), self)
        self.fullscreenShortcut.activated.connect(lambda: self.toggleFullscreenAction.toggle())
        
        # Toggle histogram visibility (H)
        self.histShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("H"), self)
        self.histShortcut.activated.connect(lambda: self.histSplitter.setSizes([1, 1000] if self.histSplitter.sizes()[0] == 0 else [0, 1]))
        
        # Toggle shapes panel (S)
        self.shapesShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("S"), self)
        self.shapesShortcut.activated.connect(lambda: self.shapeSplitter.setSizes([1000, 1] if self.shapeSplitter.sizes()[1] == 0 else [1, 0]))
        
        # Toggle analysis panel (A)
        self.analysisShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("A"), self)
        self.analysisShortcut.activated.connect(lambda: self.analysisSplitter.setSizes([1000, 1] if self.analysisSplitter.sizes()[1] == 0 else [1, 0]))
        
        # Toggle Auto-Levels (L)
        self.autoLevelsShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("L"), self)
        self.autoLevelsShortcut.activated.connect(lambda: self.histWidget.histToggle.toggle())
        
        # Redraw/Reset view (R)
        self.resetViewShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("R"), self)
        self.resetViewShortcut.activated.connect(lambda: self.viewBox.autoRange())

    def setupColorMapMenu(self):
        """
        Sets up a menu for selecting color maps from matplotlib.
        """
        self.colorMapMenu = QMenu('Color Map', self)
        color_maps = plt.colormaps()

        for cmap_name in color_maps:
            action = QAction(cmap_name, self)
            action.triggered.connect(lambda checked, name=cmap_name: self.changeColorMap(name))
            self.colorMapMenu.addAction(action)

        # Add the color map menu to the right-click context menu
        self.viewBox.menu.addMenu(self.colorMapMenu)

    def changeColorMap(self, cmap_name):
        """
        Changes the color map of the current plot.

        Parameters:
            cmap_name (str): The name of the color map to apply.
        """
        if hasattr(self, 'plotItem') and isinstance(self.plotItem, MagicPlotImageItem):
            cmap = plt.get_cmap(cmap_name)
            # Convert matplotlib colormap to a format usable by pyqtgraph
            colors = []
            positions = numpy.linspace(0, 1, 256)
            
            # Generate the colormap
            colordata = cmap(positions)
            
            # Convert to 0-255 RGBA values
            colors = (colordata * 255).astype(numpy.uint8)
            
            # Set the lookup table for the image item
            self.plotItem.setLookupTable(colors)

    def exportPlotAsImage(self):
        """
        Export the current plot as an image file.
        Supports PNG, JPG, TIFF, and PDF formats.
        """
        fileDialog = QtWidgets.QFileDialog(self)
        fileDialog.setWindowTitle("Export Plot as Image")
        fileDialog.setNameFilter("Images (*.png *.jpg *.jpeg *.tif *.tiff *.pdf)")
        fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        fileDialog.setDefaultSuffix("png")
        
        if fileDialog.exec_() == QtWidgets.QFileDialog.Accepted:
            filePath = fileDialog.selectedFiles()[0]
            
            # Create a QPixmap from the plot widget
            pixmap = QtGui.QPixmap(self.plotView.size())
            pixmap.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(pixmap)
            self.plotView.render(painter)
            painter.end()
            
            # Save the pixmap to file
            success = pixmap.save(filePath)
            if success:
                logging.info(f"Plot exported successfully to {filePath}")
            else:
                logging.error(f"Failed to export plot to {filePath}")
                QtWidgets.QMessageBox.critical(self, "Export Error", f"Failed to save image to {filePath}")
                
    def exportData(self):
        """
        Export the current plot data to a file.
        Supports CSV, NPY, and HDF5 formats (if h5py is available).
        """
        fileDialog = QtWidgets.QFileDialog(self)
        fileDialog.setWindowTitle("Export Data")
        fileDialog.setNameFilter("CSV (*.csv);;NumPy (*.npy);;HDF5 (*.h5)")
        fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        fileDialog.setDefaultSuffix("csv")
        
        if fileDialog.exec_() == QtWidgets.QFileDialog.Accepted:
            filePath = fileDialog.selectedFiles()[0]
            selectedFilter = fileDialog.selectedNameFilter()
            
            try:
                if self.data is None:
                    raise ValueError("No data to export")
                    
                # Export based on selected format
                if ".csv" in selectedFilter:
                    if self.plotMode == 1:
                        # 1D data
                        data = self.data
                        if isinstance(data, tuple) and len(data) == 2:
                            # x,y data
                            x, y = data
                            export_data = numpy.column_stack((x, y))
                            numpy.savetxt(filePath, export_data, delimiter=',', header='x,y')
                        else:
                            # Single array
                            numpy.savetxt(filePath, data, delimiter=',')
                    else:
                        # 2D data
                        numpy.savetxt(filePath, self.data, delimiter=',')
                    
                elif ".npy" in selectedFilter:
                    # Save as NumPy binary format
                    numpy.save(filePath, self.data)
                    
                elif ".h5" in selectedFilter:
                    # Try to save as HDF5 if h5py is available
                    try:
                        import h5py
                        with h5py.File(filePath, 'w') as f:
                            f.create_dataset('data', data=self.data)
                            f.attrs['date'] = str(QtCore.QDateTime.currentDateTime().toString())
                            f.attrs['plotMode'] = self.plotMode
                    except ImportError:
                        QtWidgets.QMessageBox.warning(self, "Export Warning", 
                            "H5py module not found. Data exported as NumPy binary instead.")
                        numpy.save(filePath, self.data)
                
                logging.info(f"Data exported successfully to {filePath}")
                
            except Exception as e:
                logging.error(f"Failed to export data: {str(e)}")
                QtWidgets.QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")
    
    def exportFigureSettings(self):
        """
        Export the current figure settings to a JSON file.
        These settings can be imported later to recreate the same plot appearance.
        """
        fileDialog = QtWidgets.QFileDialog(self)
        fileDialog.setWindowTitle("Export Figure Settings")
        fileDialog.setNameFilter("JSON (*.json)")
        fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        fileDialog.setDefaultSuffix("json")
        
        if fileDialog.exec_() == QtWidgets.QFileDialog.Accepted:
            filePath = fileDialog.selectedFiles()[0]
            
            try:
                import json
                
                settings = {
                    'plotMode': self.plotMode,
                    'panBounds': self._panBounds,
                    'autoLevels': self.autoLevels,
                }
                
                # Add histogram levels if applicable
                if self.plotMode == 2:
                    try:
                        levels = self.hist.getLevels()
                        settings['histLevels'] = {
                            'min': float(levels[0]),
                            'max': float(levels[1])
                        }
                    except (AttributeError, TypeError):
                        pass
                
                # Save viewBox state (position and zoom)
                try:
                    viewState = self.viewBox.getState()
                    # Convert non-serializable types to JSON-compatible format
                    if 'targetRange' in viewState:
                        viewState['targetRange'] = [
                            [float(viewState['targetRange'][0][0]), float(viewState['targetRange'][0][1])],
                            [float(viewState['targetRange'][1][0]), float(viewState['targetRange'][1][1])]
                        ]
                    settings['viewBoxState'] = viewState
                except (AttributeError, TypeError):
                    pass
                
                # Write settings to JSON file
                with open(filePath, 'w') as f:
                    json.dump(settings, f, indent=4)
                
                logging.info(f"Figure settings exported successfully to {filePath}")
                
            except Exception as e:
                logging.error(f"Failed to export figure settings: {str(e)}")
                QtWidgets.QMessageBox.critical(self, "Export Error", f"Failed to export figure settings: {str(e)}")

    def importFigureSettings(self):
        """
        Import figure settings from a JSON file and apply them to the current plot.
        """
        fileDialog = QtWidgets.QFileDialog(self)
        fileDialog.setWindowTitle("Import Figure Settings")
        fileDialog.setNameFilter("JSON (*.json)")
        fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        
        if fileDialog.exec_() == QtWidgets.QFileDialog.Accepted:
            filePath = fileDialog.selectedFiles()[0]
            
            try:
                import json
                
                with open(filePath, 'r') as f:
                    settings = json.load(f)
                
                # Apply settings
                if 'plotMode' in settings:
                    self.plotMode = settings['plotMode']
                if 'panBounds' in settings:
                    self.panBounds = settings['panBounds']
                if 'autoLevels' in settings:
                    self.autoLevels = settings['autoLevels']
                    self.histWidget.histToggle.setChecked(settings['autoLevels'])
                
                # Apply histogram levels if we're in 2D mode and there's a plotItem
                if 'histLevels' in settings and self.plotMode == 2 and hasattr(self, 'plotItem'):
                    try:
                        self.histWidget.histToggle.setChecked(False)  # Turn off auto-levels
                        self.hist.setLevels(settings['histLevels']['min'], settings['histLevels']['max'])
                        self.setLevelBoxes()
                    except Exception as e:
                        logging.warning(f"Could not apply histogram levels: {str(e)}")
                
                # Apply view box state if available
                if 'viewBoxState' in settings and hasattr(self, 'viewBox'):
                    try:
                        self.viewBox.setState(settings['viewBoxState'])
                    except Exception as e:
                        logging.warning(f"Could not apply view state: {str(e)}")
                
                logging.info(f"Figure settings imported successfully from {filePath}")
                
            except Exception as e:
                logging.error(f"Failed to import figure settings: {str(e)}")
                QtWidgets.QMessageBox.critical(self, "Import Error", f"Failed to import figure settings: {str(e)}")

    def saveSession(self):
        """
        Save the current MagicPlot session to a file, including data, 
        plot settings, histogram settings, transforms, and ROIs.
        """
        fileDialog = QtWidgets.QFileDialog(self)
        fileDialog.setWindowTitle("Save Session")
        fileDialog.setNameFilter("MagicPlot Session (*.mps)")
        fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        fileDialog.setDefaultSuffix("mps")
        
        if fileDialog.exec_() == QtWidgets.QFileDialog.Accepted:
            filePath = fileDialog.selectedFiles()[0]
            
            try:
                import pickle
                
                # Create a session dictionary with all necessary info
                session = {
                    'plotMode': self.plotMode,
                    'panBounds': self._panBounds,
                    'autoLevels': self.autoLevels,
                    'data': self.data,
                    'version': '1.0'  # For future compatibility
                }
                
                # Add histogram settings if in 2D mode
                if self.plotMode == 2:
                    try:
                        levels = self.hist.getLevels()
                        session['histLevels'] = {
                            'min': float(levels[0]),
                            'max': float(levels[1])
                        }
                    except (AttributeError, TypeError):
                        pass
                
                # Save viewBox state
                try:
                    viewState = self.viewBox.getState()
                    session['viewBoxState'] = viewState
                except AttributeError:
                    pass
                
                # Save ROI data if it exists
                try:
                    if hasattr(self, 'plotItem') and isinstance(self.plotItem, MagicPlotImageItem):
                        rois = []
                        roi_info = {}
                        
                        # Get ROIs from shapeDrawer if available
                        if hasattr(self.shapeDrawer, 'shapeHolder'):
                            for shape in self.shapeDrawer.shapeHolder.shapes:
                                if isinstance(shape, pyqtgraph.ROI):
                                    rois.append(shape)
                        
                        # Only save basic ROI properties that can be reconstructed
                        for i, roi in enumerate(rois):
                            roi_info[i] = {
                                'pos': roi.pos(),
                                'size': roi.size(),
                                'angle': roi.angle() if hasattr(roi, 'angle') else 0
                            }
                        
                        if roi_info:
                            session['rois'] = roi_info
                except Exception as e:
                    logging.warning(f"Could not save ROIs: {str(e)}")
                
                # Save to file
                with open(filePath, 'wb') as f:
                    pickle.dump(session, f)
                
                logging.info(f"Session saved successfully to {filePath}")
                
            except Exception as e:
                logging.error(f"Failed to save session: {str(e)}")
                QtWidgets.QMessageBox.critical(self, "Save Error", f"Failed to save session: {str(e)}")
    
    def loadSession(self):
        """
        Load a previously saved MagicPlot session from a file.
        """
        fileDialog = QtWidgets.QFileDialog(self)
        fileDialog.setWindowTitle("Load Session")
        fileDialog.setNameFilter("MagicPlot Session (*.mps)")
        fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        
        if fileDialog.exec_() == QtWidgets.QFileDialog.Accepted:
            filePath = fileDialog.selectedFiles()[0]
            
            try:
                import pickle
                
                with open(filePath, 'rb') as f:
                    session = pickle.load(f)
                
                # Check version compatibility
                if 'version' not in session:
                    logging.warning("Loading legacy session without version info")
                
                # Load data
                if 'data' in session and session['data'] is not None:
                    self.plot(session['data'])
                
                # Apply settings
                if 'plotMode' in session:
                    self.plotMode = session['plotMode']
                if 'panBounds' in session:
                    self.panBounds = session['panBounds']
                if 'autoLevels' in session:
                    self.autoLevels = session['autoLevels']
                    self.histWidget.histToggle.setChecked(session['autoLevels'])
                
                # Apply histogram levels if we're in 2D mode
                if 'histLevels' in session and self.plotMode == 2 and hasattr(self, 'plotItem'):
                    try:
                        self.histWidget.histToggle.setChecked(False)  # Turn off auto-levels
                        self.hist.setLevels(session['histLevels']['min'], session['histLevels']['max'])
                        self.setLevelBoxes()
                    except Exception as e:
                        logging.warning(f"Could not apply histogram levels: {str(e)}")
                
                # Apply view box state
                if 'viewBoxState' in session and hasattr(self, 'viewBox'):
                    try:
                        self.viewBox.setState(session['viewBoxState'])
                    except Exception as e:
                        logging.warning(f"Could not apply view state: {str(e)}")
                
                # Recreate ROIs if they exist
                if 'rois' in session and self.plotMode == 2:
                    try:
                        for roi_id, roi_data in session['rois'].items():
                            roi = pyqtgraph.ROI(roi_data['pos'], roi_data['size'])
                            if 'angle' in roi_data and roi_data['angle'] != 0:
                                roi.setAngle(roi_data['angle'])
                            self.plotView.addItem(roi)
                            
                            # Connect ROI signals
                            roi.sigRegionChanged.connect(lambda: self.shapeDrawer.sigShapeChanged.emit())
                            # Add to shapeHolder
                            if hasattr(self.shapeDrawer, 'shapeHolder'):
                                self.shapeDrawer.shapeHolder.shapes.append(roi)
                    except Exception as e:
                        logging.warning(f"Could not recreate ROIs: {str(e)}")
                
                logging.info(f"Session loaded successfully from {filePath}")
                
            except Exception as e:
                logging.error(f"Failed to load session: {str(e)}")
                QtWidgets.QMessageBox.critical(self, "Load Error", f"Failed to load session: {str(e)}")

 # Methods to setup plot areaD
 ##################################
    def set1dPlot(self):
        logging.debug("Set 1d Plot")
        self.deletePlotItems()
        self.plotView = pyqtgraph.PlotWidget()
        # self.plotObj = self.plotView.plotItem.plot()
        # self.plotItem = self.plotView.plotItem
        self.viewBox = self.plotView.getViewBox()
        self.viewBox.menu.addMenu(self.showMenu)
        self.viewBox.menu.addMenu(self.transformer.transMenu)
        self.viewBox.menu.addAction(self.toggleFullscreenAction)
        # Add export menu to view context menu
        self.viewBox.menu.addAction(self.exportMenuAction)
        self.analysisPane.initRegion(self.plotView)
        self.plotItems = []

    def set2dPlot(self):
        logging.debug("Set 2d Plot")
        self.deletePlotItems()
        self.plotView = pyqtgraph.PlotWidget()
        # self.plotItem = pyqtgraph.ImageItem()
        # self.plotView.addItem(self.plotItem)
        self.viewBox = self.plotView.getViewBox()
        # self.hist.setImageItem(self.plotItem)
        self.viewBox.menu.addMenu(self.showMenu)
        self.viewBox.menu.addMenu(self.transformer.transMenu)
        
        # Add the color map menu to the viewBox menu alongside other menus
        if hasattr(self, 'colorMapMenu'):
            self.viewBox.menu.addMenu(self.colorMapMenu)
        
        self.viewBox.menu.addAction(self.toggleFullscreenAction)
        # Add export menu to view context menu
        self.viewBox.menu.addAction(self.exportMenuAction)

        # lock aspect ratio to 1:1? Is there any reason not to?
        self.viewBox.setAspectLocked()

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

    def deletePlotItems(self):
        if hasattr(self, 'plotItems'):
            for i in self.plotItems:
                self.deletePlotItem(i)
        for i in reversed(range(self.plotLayout.count())):
            self.plotLayout.itemAt(i).widget().setParent(None)

    def deletePlotItem(self, item):
        self.plotItems.remove(item)
        self.plotView.removeItem(item)

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
               self.updatePanBounds()
           else:
               self._panBounds = False
               self.updatePanBounds()
        except AttributeError:
           pass

    def updatePanBounds(self, dataBounds=None, pad=100):
        if self._panBounds:
            try:
                x0 = self.viewBox.childrenBounds()[0][0]
                x1 = self.viewBox.childrenBounds()[0][1]
                y0 = self.viewBox.childrenBounds()[1][0]
                y1 = self.viewBox.childrenBounds()[1][1]
                self.viewBox.setLimits(xMin=x0  -pad,
                                        xMax=x1 + pad,
                                        yMin=y0 - pad,
                                        yMax=y1 + pad)
            except TypeError:
                pass
        else:
            self.viewBox.setLimits(xMin=None,
                                    xMax=None,
                                    yMin=None,
                                    yMax=None)

    def toggleFullscreen(self, check):
        if check:
            self.showFullScreen()
        else:
            self.showNormal()
        

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

        # These need to be integers otherwise pyqtgraph throws a warning
        mousePos_x = int(self.mousePos.x())
        mousePos_y = int(self.mousePos.y())

        # Try to index, if not then out of bounds. Don't worry about that.
        # Also ignore if no data plotted
        try:
            if self.plotMode == 1:
                value = self.data[1][mousePos_x]
            if self.plotMode == 2:
                # Only do stuff if position above 0.
                if min(mousePos_x, mousePos_y)>0:
                    value = self.data[mousePos_x,mousePos_y]

        except (IndexError, AttributeError, TypeError):
            # These all imply there is nothing plotted
            # TODO Handle this better
            pass

        if value!=None:
            self.mousePosLabel.setText ("(%d,%d) : %.2f"%
                        (mousePos_x, mousePos_y, value) )


    # Plotting methods
    #####################################

    def getImageItem(self):
        """
        Returns an empty MagicPlotImageItem and adds it to magicplot window

        Returns:
            MagicPlotImageItem: an empty MagicPlotImageItem
        """
        imageItem = MagicPlotImageItem(self)
        try:
            self.plotItems[0] = imageItem
        except IndexError:
            self.plotItems.append(imageItem)
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
        self.plotItems.append(dataItem)
        self.plot1d(dataItem)
        return dataItem

    def plot(self, *args, **kwargs):
        """
        Plot data in the MagicPlot window.

        Accepts any dimension array as arguments, and will plot in either 1D or
        2D depending on shape. Accepts data in the following formats:
        - 2D numpy array (single argument): Will be plotted as an image
        - 1D numpy array (single argument): Will be plotted as a line plot
        - Two 1D arrays: Will be plotted as x,y data
        - kwargs['downsample'] (int): Optional downsampling factor for large datasets
        - kwargs['name'] (str): Optional name for the plot item

        Parameters:
            args: Data to plot
            kwargs: Additional keyword arguments
                'downsample' (int): Downsample factor for large datasets
                'name' (str): Name for the plot item
                'panBounds' (bool): Whether to lock panning to data bounds

        Returns:
            MagicPlotDataItem: If 1D plot
            MagicPlotImageItem: If 2D plot
        """
        # Optional downsampling for large datasets to improve performance
        if 'downsample' in kwargs and kwargs['downsample'] > 1:
            downsample = kwargs.pop('downsample')
            try:
                if len(args) == 1 and args[0].ndim == 2:
                    # Downsample 2D data
                    ds_data = args[0][::downsample, ::downsample]
                    args = (ds_data,)
                    logging.info(f"Downsampled 2D data from {args[0].shape} to {ds_data.shape}")
                elif len(args) >= 1 and args[0].ndim == 1:
                    # Downsample 1D data
                    if len(args) == 1:
                        ds_data = args[0][::downsample]
                        args = (ds_data,)
                    else:
                        ds_x = args[0][::downsample]
                        ds_y = args[1][::downsample]
                        args = (ds_x, ds_y) + args[2:]
                    logging.info(f"Downsampled 1D data by factor of {downsample}")
            except (AttributeError, IndexError) as e:
                logging.warning(f"Could not downsample data: {str(e)}")

        # try 2d first
        try:
            if args[0].ndim == 2 and len(args) == 1 and args[0].shape[1] != 2:
                # Check if data is too large and warn user
                if args[0].size > 4000000:  # ~4 million pixels
                    logging.warning(f"Large dataset ({args[0].shape}): Consider using 'downsample' parameter for better performance")

                dataItem = MagicPlotImageItem(self, *args, **kwargs)

                if self.plotMode != 2:
                    self.plotMode = 2

                # make sure we don't have more than a single 2d plotitem in the list
                try:
                    self.plotItems[0] = dataItem
                except IndexError:
                    self.plotItems.append(dataItem)

                # clear the view then add new dataItem
                self.plotView.clear()
                self.plot2d(dataItem)
                self.data = dataItem.image
                self.dataUpdateSignal2d.emit(self.data)

            else:
                # data doesn't match 2D data spec
                raise IndexError('Given data does not fit 2D plot specification')

        except (IndexError, AttributeError):
            # this usually means the data is 1D so try to plot 1D
            try:
                # Check if data is too large and warn user
                if len(args) > 0 and hasattr(args[0], 'size') and args[0].size > 100000:
                    logging.warning(f"Large dataset ({args[0].size} points): Consider using 'downsample' parameter for better performance")
                
                # Try to plot 1d
                dataItem = MagicPlotDataItem(self, *args, **kwargs)

                if self.plotMode != 1 and not dataItem.overlay:
                    self.plotMode = 1

                self.plotItems.append(dataItem)
                self.plot1d(dataItem)
                self.data = dataItem.getData()
                self.dataUpdateSignal1d.emit(self.data)

            except Exception as e:
                # This means the data is unplottable by pyqtgraph
                logging.error(f'Unable to plot 1D or 2D, check data: {str(e)}')
                raise

        # Automatically scale the view to fit the data
        if self.plotMode == 1:
            self.viewBox.autoRange()
        elif self.plotMode == 2:
            self.viewBox.autoRange()

        # lock panning to plot area
        if 'panBounds' in kwargs.keys():
            self.panBounds = kwargs['panBounds']

        if self._panBounds:
            self.updatePanBounds()

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
        self.plotItems[-1].scene().sigMouseMoved.connect(
                self.mousePosMoved)
        self.shapeDrawer.setView(self.plotView, self.plotItems)
        self.updatePanBounds()
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
        self.shapeDrawer.setView(self.plotView, self.plotItems)
        self.updatePanBounds()
        self.viewBox.autoRange()

    def updatePlot(self):
        """
        Updates the plot with the latest data.
        
        This is a more efficient replacement for the previous implementation
        that used QApplication.processEvents() for live plotting.
        Instead, this implementation uses a timer to schedule updates
        at appropriate intervals, reducing CPU usage.
        """
        if not hasattr(self, 'update_timer'):
            self.update_timer = QtCore.QTimer()
            self.update_timer.timeout.connect(lambda: None)  # Just trigger event loop
            self.update_timer.setSingleShot(True)
        
        if not self.update_timer.isActive():
            self.update_timer.start(16)  # ~60 FPS


    def dataUpdateHandler(self, data):
        """
        Connected to the dataUpdate1d and dataUpdate2d signals, handles
        updating data in the plot.
        """
        self.analysisPane.runPluginSignal.emit(data)
        # Only update histogram bounds if autoLevels is enabled
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
        # Block signals temporarily to prevent automatic updates
        self.hist.blockSignals(True)
        
        # Connect the image item to the histogram
        self.hist.setImageItem(imageItem)
        
        # Get current levels
        levels = imageItem.getLevels()
        
        try:
            # Set the levels in the histogram and spin boxes
            self.hist.setLevels(levels[0], levels[1])
            self.histWidget.maxLevelBox.setValue(levels[1])
            self.histWidget.minLevelBox.setValue(levels[0])
            
            # Set the auto-levels checkbox state
            self.histWidget.histToggle.setChecked(self.autoLevels)
            
            # Tell the image item whether to use auto-levels
            imageItem.setOpts(autoLevels=self.autoLevels)
            
            # Only connect sigLevelsChanged to histToggle.click if autoLevels is True
            if self.autoLevels:
                self.hist.sigLevelsChanged.connect(self.histWidget.histToggle.click)
        except TypeError:
            logging.info('Empty ImageItem')
        
        # Unblock signals after setup is complete
        self.hist.blockSignals(False)

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
                # Disconnect auto-levels behavior
                try:
                    self.hist.sigLevelsChanged.disconnect(self.histWidget.histToggle.click)
                except TypeError:
                    logging.debug('Histogram connection already removed')
                    
                # Save current levels
                levels = self.plotItem.getLevels()
                
                # Disable auto-levels on the image item
                self.plotItem.setOpts(autoLevels=False)
                
                # Connect signals to ensure manual changes are applied
                self.plotItem.sigImageChanged.connect(self.setLevelsFromHist)
                self.hist.sigLevelsChanged.connect(self.setLevelBoxes)
                
                # Set the levels to current values
                self.hist.setLevels(levels[0], levels[1])
            else:
                # Enable auto-levels
                self.plotItem.setOpts(autoLevels=True)
                
                # Get current image data
                im = self.plotItem.image
                if im is not None:
                    # Set levels to min/max of current data
                    self.plotItem.setLevels((im.min(), im.max()))
                    
                    # Disconnect manual level update
                    try:
                        self.plotItem.sigImageChanged.disconnect(self.setLevelsFromHist)
                    except TypeError:
                        logging.debug('Histogram not connected so cannot disconnect')
                        
                    # Update histogram to match new levels
                    self.hist.setLevels(im.min(), im.max())
                    
                    # Connect auto-levels behavior
                    self.hist.sigLevelsChanged.connect(self.histWidget.histToggle.click)
        except TypeError as e:
            logging.error(f"Error in activateHistogram: {str(e)}")
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
        # Only update histogram levels if autoLevels is enabled
        if not self.autoLevels:
            return
            
        try:
            self.hist.blockSignals(True)
            _min, _max = data.min(), data.max()
            self.hist.setLevels(_min, _max)
            self.setLevelBoxes()
            self.hist.blockSignals(False)
        except AttributeError:
            # usually means trying to udpate hist with 1d data
            pass

    def cleanupMemory(self):
        """
        Free up memory by clearing cached data and encouraging garbage collection.
        This is useful when working with very large datasets to prevent memory issues.
        """
        import gc
        
        # Clear references to unused ROI windows
        if hasattr(self, 'plotItem') and isinstance(self.plotItem, MagicPlotImageItem):
            # Clean up any closed windows from the ROI windows dictionary
            for roi, (window, plt) in list(self.plotItem.roi_windows.items()):
                if not window.isVisible():
                    logging.debug(f"Removing closed ROI window from memory")
                    self.plotItem.roi_windows.pop(roi)
            
            # Clean up legacy windows list
            self.plotItem.windows = [w for w in self.plotItem.windows if w[0].isVisible()]
        
        # Clear transform cache if it exists
        if hasattr(self.transformer, 'cache'):
            self.transformer.cache = {}
            
        # Run garbage collection
        gc.collect()
        
        logging.info("Memory cleanup performed")

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

        if 'name' in kwargs.keys():
            self._name = kwargs['name']
        else:
            self._name = '2DPlotItem'

        super(MagicPlotImageItem, self).__init__(*args, **kwargs)
        self.windows = []
        # Dictionary to track existing ROI windows
        self.roi_windows = {}
        self.sigImageChanged.connect(self.updateWindows)
        self.parent.transformer.worker.emitter.sigWorkerFinished.connect(super(MagicPlotImageItem, self).setImage)

    def setData(self, data, **kwargs):
        """
        Wrapper for pyqtgraph.ImageItem.setImage() to make it consistent with
        pyqtgraph.PlotDataItem.setData()
        
        Parameters:
            data (numpy.ndarray): The image data to be displayed
            **kwargs: Additional keyword arguments passed to setImage
        
        Raises:
            ValueError: If data is not a valid numpy array
        """
        if data is None:
            logging.warning("Attempting to set None as image data")
        elif not isinstance(data, numpy.ndarray):
            raise ValueError(f"Expected numpy.ndarray, got {type(data)}")
            
        self.setImage(image=data, **kwargs)

    def setImage(self, image=None, **kwargs):
        """
        Extension of pyqtgraph.ImageItem.setImage() to allow transforms to be
        applied to the data before it is plotted.
        """
        # transform if transformer is active
        if self.parent.transformer.active and image is not None:
            self.parent.transformer.transform(image)
            return

        # Save current levels if autoLevels is disabled and we're updating with new data
        current_levels = None
        if hasattr(self.parent, 'autoLevels') and not self.parent.autoLevels and image is not None:
            current_levels = self.getLevels()
            # Force autoLevels to False in kwargs to ensure it's not overridden
            kwargs['autoLevels'] = False
        elif image is not None and 'autoLevels' not in kwargs:
            # Otherwise respect the parent's setting
            kwargs['autoLevels'] = self.parent.autoLevels

        # call the pyqtgraph.ImageItem.setImage() function
        super(MagicPlotImageItem, self).setImage(image, **kwargs)
        
        # Restore saved levels if autoLevels is disabled
        if current_levels is not None:
            self.setLevels(current_levels)

    def informViewBoundsChanged(self):
        super(MagicPlotImageItem, self).informViewBoundsChanged()
        if self.parent._panBounds:
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
        If the ROI has been plotted before, update the existing window instead
        of creating a new one.

        Parameters:
            roi (pyqtgraph.ROI): Region of Interest to use for plotting
            
        Returns:
            MagicPlot: The window containing the plotted ROI data
        """
        # Get ROI data
        sliceData = roi.getArrayRegion(self.image, self)
        
        # Check if we already have a window for this ROI
        if roi in self.roi_windows:
            # Update existing window
            window, plt = self.roi_windows[roi]
            plt.setData(sliceData)
        else:
            # Create new window
            window = MagicPlot()
            plt = window.plot(sliceData)
            window.show()
            # Store in both the dictionary and the list (for backward compatibility)
            self.roi_windows[roi] = (window, plt)
            self.windows.append([window, plt, roi])
            
        return window

    def updateWindows(self):
        """
        Update all ROI plots when the parent image changes.
        
        Uses both the legacy list-based approach and the new dictionary-based approach
        to ensure backward compatibility while providing the improved functionality.
        """
        # Update windows from the dictionary (new approach)
        for roi, (window, plt) in list(self.roi_windows.items()):
            try:
                sliceData = roi.getArrayRegion(self.image, self)
                plt.setData(sliceData)
            except Exception as e:
                logging.debug(f"Error updating ROI window: {str(e)}")
                # Remove from dictionary if there's an error
                self.roi_windows.pop(roi, None)
        
        # Also update from the list for backward compatibility
        for i in list(self.windows):  # Create a copy of the list to safely modify during iteration
            try:
                window, plt, roi = i
                sliceData = roi.getArrayRegion(self.image, self)
                plt.setData(sliceData)
            except:
                logging.debug("ROI doesn't exist, removing window from list")
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

    def name(self):
        """
        Added for parity with DataItem, which has a name method that can be 
        set using keyword argument 'name'
        """
        return self._name

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
            super(MagicPlotDataItem, self).setData(data, **kwargs)
            return
    """
    def __init__(self, parent, *args, **kwargs):
        # setData with pyqtgraph.PlotDataItem.setData()
        self.parent = parent
        super(MagicPlotDataItem, self).__init__(*args, **kwargs)

        # if item is to be plotted over a 2D plot
        if 'overlay' in kwargs.keys():
            self.overlay = kwargs['overlay']
        else:
            self.overlay = False
        
        # define PlotDataItem to handle transforming data
        self.transformItem = pyqtgraph.PlotDataItem()

        self.originalData = self.getData()
        if not self.overlay:
            self.parent.transformer.worker.emitter.sigWorkerFinished.connect(super(MagicPlotDataItem, self).setData)


    def informViewBoundsChanged(self):
        super(MagicPlotDataItem, self).informViewBoundsChanged()
        if self.parent._panBounds:
            self.parent.updatePanBounds(dataBounds=[self.dataBounds(0), self.dataBounds(1)])

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

    def setData(self, *args, **kwargs):
        # transform if transformer is active
        if self.parent.transformer.active and not self.overlay:
            self.transformItem.setData(*args, **kwargs)
            self.parent.transformer.transform(self.transformItem.getData())
            return

        super(MagicPlotDataItem, self).setData(*args, **kwargs)

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
            self.setData(self.getData()[0], self.getData()[1])
        else:
            self.setData(self.originalData[0], self.originalData[1])
            self.originalData = None

    def updatePlot(self):
        """
        Updates the plot with the latest data.
        
        This is a more efficient implementation using a timer-based approach
        rather than directly calling processEvents().
        """
        if not hasattr(self.parent, 'update_timer'):
            self.parent.update_timer = QtCore.QTimer()
            self.parent.update_timer.timeout.connect(lambda: None)
            self.parent.update_timer.setSingleShot(True)
        
        if not self.parent.update_timer.isActive():
            self.parent.update_timer.start(16)  # ~60 FPS

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication([])
    w = MagicPlot()
    w.plot(numpy.random.random((50,50)))
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
