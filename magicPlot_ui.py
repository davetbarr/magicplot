# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/apr/CfAI/magicPlot/magicPlot.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MagicPlot(object):
    def setupUi(self, MagicPlot):
        MagicPlot.setObjectName(_fromUtf8("MagicPlot"))
        MagicPlot.resize(579, 486)
        self.gridLayout = QtGui.QGridLayout(MagicPlot)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.drawSplitter = QtGui.QSplitter(MagicPlot)
        self.drawSplitter.setOrientation(QtCore.Qt.Horizontal)
        self.drawSplitter.setHandleWidth(2)
        self.drawSplitter.setObjectName(_fromUtf8("drawSplitter"))
        self.verticalLayoutWidget_2 = QtGui.QWidget(self.drawSplitter)
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        self.plotContainerLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.plotContainerLayout.setObjectName(_fromUtf8("plotContainerLayout"))
        self.plotLayout = QtGui.QHBoxLayout()
        self.plotLayout.setObjectName(_fromUtf8("plotLayout"))
        self.plotContainerLayout.addLayout(self.plotLayout)
        self.mousePosLabel = QtGui.QLabel(self.verticalLayoutWidget_2)
        self.mousePosLabel.setText(_fromUtf8(""))
        self.mousePosLabel.setObjectName(_fromUtf8("mousePosLabel"))
        self.plotContainerLayout.addWidget(self.mousePosLabel)
        self.gridLayout.addWidget(self.drawSplitter, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.plotRand1d = QtGui.QPushButton(MagicPlot)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotRand1d.sizePolicy().hasHeightForWidth())
        self.plotRand1d.setSizePolicy(sizePolicy)
        self.plotRand1d.setObjectName(_fromUtf8("plotRand1d"))
        self.horizontalLayout.addWidget(self.plotRand1d)
        self.plotRand2d = QtGui.QPushButton(MagicPlot)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotRand2d.sizePolicy().hasHeightForWidth())
        self.plotRand2d.setSizePolicy(sizePolicy)
        self.plotRand2d.setObjectName(_fromUtf8("plotRand2d"))
        self.horizontalLayout.addWidget(self.plotRand2d)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.retranslateUi(MagicPlot)
        QtCore.QMetaObject.connectSlotsByName(MagicPlot)

    def retranslateUi(self, MagicPlot):
        MagicPlot.setWindowTitle(_translate("MagicPlot", "Form", None))
        self.plotRand1d.setText(_translate("MagicPlot", "1-D Random", None))
        self.plotRand2d.setText(_translate("MagicPlot", "2-D Random", None))

