from __future__ import division
# Try importing PyQt5, if not fall back to PyQt4
try:
    from PyQt5 import QtCore, QtGui, QtWidgets, uic
    PYQTv = 5
except ImportError:
    from PyQt4 import QtCore, QtGui, uic
    QtWidgets = QtGui
    PyQTv = 4
# from PyQt4 import QtCore, QtGui
from . import transformPlugins

import copy

class Transformer(QtCore.QObject):
    """
    Controls transformation of data using MagicPlot TransformPlugins.

    Attributes:
        tList (transformPlugins.TransformList): List of available transforms
        aList (transformPlugins.TransformList): List of applied transforms
        active (bool): if True, then transforms are applied
        dialog (transformPlugins.TransformDialog): Dialog showing tList and aList,
            where the user can drag and drop from available to applied transforms
    """
    sigActiveToggle = QtCore.pyqtSignal(bool)
    def __init__(self):
        super(Transformer, self).__init__()
        self.tList = transformPlugins.TransformList(None)
        self.tList.getTransforms()
        self.aList = transformPlugins.TransformList(self.tList)
        self.active = False
        self.initContextMenu()

    def initContextMenu(self):
        """
        Right-click context menu shown under 'Transforms'
        """
        self.transMenu = QtGui.QMenu('Transforms')
        runTransforms = QtGui.QAction('Activate Transforms', self)
        runTransforms.setCheckable(True)
        runTransforms.toggled.connect(self.toggleRunning)
        self.transMenu.addAction(runTransforms)
        openDialog = QtGui.QAction('Open Transforms dialog', self)
        openDialog.triggered.connect(self.openDialog)
        self.transMenu.addAction(openDialog)
        self.transMenu.addSeparator()

        # add transforms to list below other options so they can be
        # quickly selected and applied
        self.quickTransforms = QtGui.QActionGroup(self)
        for row, plugin in enumerate(self.tList):
            action = QtGui.QAction(plugin.name, self.quickTransforms)
            action.setData(row)
            self.transMenu.addAction(action)
        self.quickTransforms.triggered.connect(self.addFromContextMenu)

    def addFromContextMenu(self, action):
        """
        Use one of the quick transformations to transform data.
        This automatically enables transforms if they are not already
        active.
        """
        activeCheck = self.transMenu.actions()[0]
        if self.aList.rowCount() != 0:
            self.aList.clear()
            activeCheck.setChecked(False)
        row = action.data()
        self.aList.append(self.tList[row])
        activeCheck.setChecked(True)

    def transform(self, data):
        """
        Transform data by applying the transforms in the applied
        transforms list in order.

        Parameters:
            data (numpy.ndarray, tuple[numpy.ndarray]): the data to be
                transformed.

        Returns:
            numpy.ndarray: the transformed data
        """
        if self.active:
            for i in self.aList:
                i.setData(data)
                data = i.run()
            return data
        else:
            return data

    def openDialog(self):
        """
        Open the transforms dialog
        """
        self.dialog = transformPlugins.TransformDialog(tList=self.tList,
                aList=self.aList)
        self.dialog.show()

    def toggleRunning(self, checked):
        """
        Handles the activate transforms menu option
        """
        self.active = checked
        self.sigActiveToggle.emit(checked)
