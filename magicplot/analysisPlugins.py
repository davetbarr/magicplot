from PyQt4 import QtGui, QtCore
import numpy

class AnalysisPlugin(QtGui.QWidget):
    """
    Base class for analysis plugins to MagicPlot.
    """
    sigSetInputs = QtCore.pyqtSignal(object)
    sigSetOutputs = QtCore.pyqtSignal(object)
    sigSetUserInputs = QtCore.pyqtSignal(object)

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
        Input: self.data is what is displayed in the MagicPlot window,
            either (x,y) for 1D or array(N,N) for 2D

        Output: user must return a dict of outputs, for example:

            return {'out1': out1, 'out2': out2}
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


class Average(AnalysisPlugin):

    def __init__(self):
        super(Average, self).__init__(params={'param1':0, 'param2':42},
            name='Average')

    def run(self):
        if len(self.data) != 2:
            raise Exception('Only works with 1D plots')
        return {'Average': numpy.average(self.data[1][self.params['param1']:self.params['param2']])}

class ShowData(AnalysisPlugin):

    def __init__(self):
        super(ShowData, self).__init__(name='Data')

    def run(self):
        return {'Data': self.data}
