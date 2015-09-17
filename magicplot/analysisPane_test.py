import sys
import os
import importlib
# SRC_PATH = os.path.dirname(os.path.abspath(__file__))
# os.system("pyuic4 {0}/analysisPane.ui > {0}/analysisPane_ui.py".format(SRC_PATH))

from analysisPlugins import AnalysisPlugin

from PyQt4 import QtCore, QtGui
import pyqtgraph
import numpy
import magicplot
from scipy.stats import linregress

# Get this files path so we can get plugin
import os
PATH = os.path.dirname(os.path.abspath(__file__))

class AnalysisPane(QtGui.QTabWidget):

    def __init__(self, parent=None, view=None, item=None):
        super(AnalysisPane, self).__init__(parent)
        self.getPluginList()
        self.setupUi()
        self.data = None

    def setupUi(self):
        for i in self.pluginList:
            i.generateUi()
            self.addTab(i, i.name)

    def getPluginList(self):
        self.pluginList = []
        path = os.path.abspath(os.path.join(PATH, '../plugins'))
        for i in os.listdir(path):
            fname = os.path.join(path, i)
            with open(fname, 'r') as f:
                exec(f)
                self.pluginList.append(Plugin())

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
