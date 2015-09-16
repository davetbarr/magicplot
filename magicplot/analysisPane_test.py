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

    def setupUi(self):
        pluginList = [analysisPlugins.TestPlugin()]
        for i in pluginList:
            i.generateUi()
            self.addTab(i, 'TestPlugin')

    def getPluginList(self):
        # return pluginList
        pass
