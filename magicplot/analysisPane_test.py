import sys
import os
# SRC_PATH = os.path.dirname(os.path.abspath(__file__))
# os.system("pyuic4 {0}/analysisPane.ui > {0}/analysisPane_ui.py".format(SRC_PATH))

import analysisPlugins

from PyQt4 import QtCore, QtGui
import pyqtgraph
import numpy
import magicplot
from scipy.stats import linregress


class AnalysisPane(QtGui.QTabWidget):

    def __init__(self, parent=None, view=None, item=None):
        super(AnalysisPane, self).__init__(parent)
        self.setupUi()
        self.data = None

    def setupUi(self):
        self.pluginList = [analysisPlugins.Average(), analysisPlugins.ShowData()]
        for i in self.pluginList:
            i.generateUi()
            self.addTab(i, i.name)

    def getPluginList(self):
        # return pluginList
        pass

    def updateData(self, data):
        for i in self.pluginList:
            i.setData(data)
        self.runPlugins()

    def runPlugins(self):
        for i in self.pluginList:
            i.setParams()
            try:
                output = i.run()
                i.outputBox.setText(str(output))
            except Exception as e:
                i.outputBox.setText(e.message)
