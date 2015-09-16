from PyQt4 import QtGui, QtCore
import numpy

class AnalysisPlugin(QtGui.QWidget):
    """
    Base class for analysis plugins to MagicPlot.
    """

    def __init__(self, outputs={}, inputs={}, userInputs={}):
        super(AnalysisPlugin, self).__init__()
        self.inputs = inputs
        self.outputs = outputs
        self.userInputs = userInputs

    def setInputs(self, inputs):
        self.inputs = inputs

    def setOutputs(self, outputs):
        self.output = outputs

    def setUserInputs(self, userInputs):
        self.userInputs = userInputs

    def run(self, inputs):
        """
        Must take dict inputs and return dict outputs
        """
        pass

    def generateUi(self):
        self.layout = QtGui.QGridLayout()
        for i in self.inputs.keys():
            label = QtGui.QLabel(i)
            display = QtGui.QLabel(self.inputs[i])
            self.layout.addWidget(label)
            self.layout.addWidget(display)
        for i in self.userInputs.keys():
            label = QtGui.QLabel(i)
            box = QtGui.QDoubleSpinBox()
            self.layout.addWidget(label)
            self.layout.addWidget(box)
        for i in self.outputs.keys():
            label = QtGui.QLabel(i)
            display = QtGui.QLabel(self.outputs[i])
            self.layout.addWidget(label)
            self.layout.addWidget(display)
        self.setLayout(self.layout)


class TestPlugin(AnalysisPlugin):

    def __init__(self):
        outputs = {'Average':None}
        inputs = {'data':None}
        super(TestPlugin, self).__init__(outputs=outputs, inputs=inputs)

    def run(self, inputs):
        return {'Average': numpy.average(inputs['data'])}
