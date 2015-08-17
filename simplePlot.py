from PyQt4 import QtGui, QtCore
import sys
import numpy
import pyqtgraph

class Widget(QtGui.QWidget):

    def __init__(self):
        super(Widget, self).__init__()

        self.initUI()

    def initUI(self):

        self.resize(300,300)
        self.move(300,300)
        self.setWindowTitle('test')
        self.plotLayout = QtGui.QHBoxLayout()
        self.setLayout(self.plotLayout)


    def plot(self, x, y, data, threeDdata):

        self.plotView = pyqtgraph.PlotWidget()
        self.plotLayout.addWidget(self.plotView)
        self.plotView.plot(x,y)

        self.twoDplotView = pyqtgraph.ImageView()
        self.plotLayout.addWidget(self.twoDplotView)
        self.twoDplotView.setImage(data)

        self.threeDplotView = pyqtgraph.ImageView()
        self.plotLayout.addWidget(self.threeDplotView)
        self.threeDplotView.setImage(threeDdata)


def main():
    app = QtGui.QApplication(sys.argv)

    test = Widget()


    data = numpy.random.random(100)
    twoDdata = numpy.random.random((100,100))
    threeDdata = numpy.random.random((100,100,100))
    x = numpy.arange(100)
    test.plot(x, data, twoDdata, threeDdata)
    test.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
