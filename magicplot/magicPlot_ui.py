# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/apr/CfAI/magicPlot/magicplot/magicPlot.ui'
#
# Created: Mon Sep 14 15:29:54 2015
#      by: PyQt4 UI code generator 4.11.3
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
        MagicPlot.resize(658, 600)
        self.gridLayout = QtGui.QGridLayout(MagicPlot)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.analysisSplitter = QtGui.QSplitter(MagicPlot)
        self.analysisSplitter.setOrientation(QtCore.Qt.Vertical)
        self.analysisSplitter.setObjectName(_fromUtf8("analysisSplitter"))
        self.drawSplitter = QtGui.QSplitter(self.analysisSplitter)
        self.drawSplitter.setOrientation(QtCore.Qt.Horizontal)
        self.drawSplitter.setHandleWidth(2)
        self.drawSplitter.setObjectName(_fromUtf8("drawSplitter"))
        self.verticalLayoutWidget_2 = QtGui.QWidget(self.drawSplitter)
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        self.plotContainerLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.plotContainerLayout.setMargin(0)
        self.plotContainerLayout.setObjectName(_fromUtf8("plotContainerLayout"))
        self.plotLayout = QtGui.QHBoxLayout()
        self.plotLayout.setObjectName(_fromUtf8("plotLayout"))
        self.plotContainerLayout.addLayout(self.plotLayout)
        self.mousePosLabel = QtGui.QLabel(self.verticalLayoutWidget_2)
        self.mousePosLabel.setText(_fromUtf8(""))
        self.mousePosLabel.setObjectName(_fromUtf8("mousePosLabel"))
        self.plotContainerLayout.addWidget(self.mousePosLabel)
        self.gridLayout.addWidget(self.analysisSplitter, 0, 0, 1, 1)

        self.retranslateUi(MagicPlot)
        QtCore.QMetaObject.connectSlotsByName(MagicPlot)

    def retranslateUi(self, MagicPlot):
        MagicPlot.setWindowTitle(_translate("MagicPlot", "Form", None))

