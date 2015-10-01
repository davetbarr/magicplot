"""
================
Analysis Plugins
================

Analysis plugins use data that is currently plotted in the MagicPlot. To write a
plugin, simply inherit the base class ``AnalysisPlugin`` and provide at the
minimum an ``__init__`` and a ``run()`` function. In the ``__init__`` function
any parameters that the analysis routine requires and their defualt values
should be set as a dictionary, and the name of the plugin should be set. This is
done by calling ``__init__`` on the base class:: 

    def __init__(self):
        AnalysisPlugin.__init__(params={'param1': param1, 'param2': param2},
            name='MyPlugin')

``numpy`` is already imported, but if you need other modules for analysis then
import them in ``__init__``

The ``run()`` method of your plugin should take ``self.data`` and return some
data, this will be displayed in the output box in the analysis pane. You can get
any required parameters from ``self.params``, which is a dictionary of current
parameter values::

    def run(self):
        input = self.data
        param1, param2 = self.params['param1'], self.params['param2']
        output = doSomeAnalysis(input, param1, param2)
        return output

Place ``MyPlugin.py`` into the ``MagicPlot/plugins/analysis`` directory and it
will be autodetected by MagicPlot.

See the example plugins for more information.
"""
from PyQt4 import QtGui, QtCore
import numpy

class AnalysisPlugin(QtGui.QWidget):
    """
    Base class for analysis plugins for MagicPlot.
    """

    def __init__(self, params={}, name='Plugin'):
        super(AnalysisPlugin, self).__init__()
        self.params = params
        self.name = name

    def setData(self, data):
        self.data = data

    def setParams(self):
        for i in self.paramBoxList.keys():
            self.params[i] = self.paramBoxList[i].value()

    def run(self):
        """
        ``self.data`` is what is displayed in the MagicPlot window,
        either ``(x,y)`` for 1D or ``array(N,N)`` for 2D

        Whatever is returned is displayed in the output QTextBox
        """
        pass

    def generateUi(self):
        self.layout = QtGui.QGridLayout()
        self.paramBoxList = {}
        for i in self.params.keys():
            label = QtGui.QLabel(i)
            box = QtGui.QDoubleSpinBox()
            box.setValue(self.params[i])
            box.valueChanged.connect(self.setParams)
            self.paramBoxList[i] = box
            self.layout.addWidget(label)
            self.layout.addWidget(box)
        self.outputBox = QtGui.QTextEdit()
        self.layout.addWidget(self.outputBox, 0, 1, 2*len(self.params), 1)
        self.setLayout(self.layout)
