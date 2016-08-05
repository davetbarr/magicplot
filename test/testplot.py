import os
import sys
FILE_PATH = os.path.dirname(os.path.realpath(__file__))
MPLOT_PATH = os.path.join(FILE_PATH, "..")

import sys
sys.path.append(MPLOT_PATH)

import magicplot
# Try importing PyQt5, if not fall back to PyQt4
try:
    from PyQt5 import QtCore, QtGui, QtWidgets, uic
    PYQTv = 5
except (ImportError, RuntimeError):
    from PyQt4 import QtCore, QtGui, uic
    QtWidgets = QtGui
    PyQTv = 4

try:
    __IPYTHON__
except NameError:
    __IPYTHON__=False




if __name__ == "__main__":

    app = QtWidgets.QApplication([])

    mplot = magicplot.MagicPlot()   

    mplot.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        if not __IPYTHON__:
            QtWidgets.QApplication.instance().exec_()