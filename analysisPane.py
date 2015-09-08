import sys
import os
SRC_PATH = os.path.dirname(os.path.abspath(__file__))
os.system("pyuic4 {0}/analysisPane.ui > {0}/analysisPane_ui.py".format(SRC_PATH))

import analysisPane_ui

from PyQt4 import QtCore, QtGui
import pyqtgraph
import numpy
import magicPlot

class AnalysisPane(QtGui.QTabWidget, analysisPane_ui.Ui_AnalysisPane):

    def __init__(self, parent=None, view=None, item=None):
        super(AnalysisPane, self).__init__(parent)
        self.setupUi(self)
        self.checkRegion.toggled.connect(self.regionToggle)
        self.setView(view, item)

    def updateBoxes(self, args):
        x1, x2 = self.region.getRegion()
        self.x1Box.setValue(x1)
        self.x2Box.setValue(x2)
        self.region.setData(self.data)
        self.gradient()

    def updateRegion(self):
        x1 = self.x1Box.value()
        x2 = self.x2Box.value()
        self.region.setRegion((x1,x2))
        self.region.setData(self.data)
        self.gradient()

    def updateData(self, data):
        self.data = data
        self.region.setData(data)
        self.gradient()

    def setView(self, view, item):
        self.plotView = view
        self.plotItem = item
        self.region = Region()
        self.region.setVisible(False)

    def regionToggle(self, checked):
        if checked:
            self.region.setVisible(True)
            self.plotView.addItem(self.region)
            self.updateBoxes(self)
            self.region.sigRegionChanged.connect(self.updateBoxes)
            self.updateButton.clicked.connect(self.updateRegion)
            self.gradient()
        else:
            self.region.setVisible(False)
            self.gradient()

    def gradient(self):
        if self.region.isVisible():
            data = self.region.data
        else:
            data = self.data
        gradient = (data[-1] - data[0])/len(data)
        self.gradientDisplay.setText("{:f}".format(gradient))

class Region(pyqtgraph.LinearRegionItem):

    def __init__(self):
        super(Region, self).__init__()

    def setData(self, data):
        x1, x2 = self.getRegion()
        self.data = data[x1:x2]
