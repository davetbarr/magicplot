import os
import sys
FILE_PATH = os.path.dirname(os.path.realpath(__file__))
MPLOT_PATH = os.path.join(FILE_PATH, "..")

import sys
sys.path.append(MPLOT_PATH)

import magicplot
from PyQt5 import QtWidgets

if __name__ == "__main__":

    app = QtWidgets.QApplication([])

    mplot = magicplot.MagicPlot()   

    mplot.show()