# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ojdf/Documents/MagicPlot/magicPlot.ui'
#
# Created: Wed Aug 26 17:24:39 2015
#      by: PyQt4 UI code generator 4.10.4
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
        MagicPlot.resize(642, 600)
        self.gridLayout = QtGui.QGridLayout(MagicPlot)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.drawSplitter = QtGui.QSplitter(MagicPlot)
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
        self.gridLayout.addWidget(self.drawSplitter, 0, 0, 1, 1)
        self.maxSlider = QtGui.QSlider(MagicPlot)
        self.maxSlider.setMaximum(255)
        self.maxSlider.setProperty("value", 255)
        self.maxSlider.setOrientation(QtCore.Qt.Vertical)
        self.maxSlider.setObjectName(_fromUtf8("maxSlider"))
        self.gridLayout.addWidget(self.maxSlider, 0, 1, 1, 1)
        self.minSlider = QtGui.QSlider(MagicPlot)
        self.minSlider.setMaximum(255)
        self.minSlider.setOrientation(QtCore.Qt.Vertical)
        self.minSlider.setObjectName(_fromUtf8("minSlider"))
        self.gridLayout.addWidget(self.minSlider, 0, 2, 1, 1)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setHorizontalSpacing(6)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.getLiveData = QtGui.QCheckBox(MagicPlot)
        self.getLiveData.setObjectName(_fromUtf8("getLiveData"))
        self.gridLayout_2.addWidget(self.getLiveData, 1, 2, 1, 1)
        self.openFitsFile = QtGui.QPushButton(MagicPlot)
        self.openFitsFile.setObjectName(_fromUtf8("openFitsFile"))
        self.gridLayout_2.addWidget(self.openFitsFile, 1, 1, 1, 1)
        self.plot1dRealtime = QtGui.QPushButton(MagicPlot)
        self.plot1dRealtime.setObjectName(_fromUtf8("plot1dRealtime"))
        self.gridLayout_2.addWidget(self.plot1dRealtime, 0, 2, 1, 1)
        self.plotRand2d = QtGui.QPushButton(MagicPlot)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotRand2d.sizePolicy().hasHeightForWidth())
        self.plotRand2d.setSizePolicy(sizePolicy)
        self.plotRand2d.setObjectName(_fromUtf8("plotRand2d"))
        self.gridLayout_2.addWidget(self.plotRand2d, 0, 1, 1, 1)
        self.bufferSizeSlider = QtGui.QSlider(MagicPlot)
        self.bufferSizeSlider.setMouseTracking(False)
        self.bufferSizeSlider.setMinimum(10)
        self.bufferSizeSlider.setMaximum(100)
        self.bufferSizeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.bufferSizeSlider.setTickPosition(QtGui.QSlider.NoTicks)
        self.bufferSizeSlider.setTickInterval(1)
        self.bufferSizeSlider.setObjectName(_fromUtf8("bufferSizeSlider"))
        self.gridLayout_2.addWidget(self.bufferSizeSlider, 0, 3, 1, 1)
        self.plotSelected = QtGui.QPushButton(MagicPlot)
        self.plotSelected.setObjectName(_fromUtf8("plotSelected"))
        self.gridLayout_2.addWidget(self.plotSelected, 1, 0, 1, 1)
        self.subApDraw = QtGui.QCheckBox(MagicPlot)
        self.subApDraw.setObjectName(_fromUtf8("subApDraw"))
        self.gridLayout_2.addWidget(self.subApDraw, 1, 3, 1, 1)
        self.plotRand1d = QtGui.QPushButton(MagicPlot)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotRand1d.sizePolicy().hasHeightForWidth())
        self.plotRand1d.setSizePolicy(sizePolicy)
        self.plotRand1d.setObjectName(_fromUtf8("plotRand1d"))
        self.gridLayout_2.addWidget(self.plotRand1d, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 1, 0, 1, 1)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.drawCentroids = QtGui.QCheckBox(MagicPlot)
        self.drawCentroids.setObjectName(_fromUtf8("drawCentroids"))
        self.gridLayout_3.addWidget(self.drawCentroids, 0, 0, 1, 1)
        self.drawArr = QtGui.QCheckBox(MagicPlot)
        self.drawArr.setObjectName(_fromUtf8("drawArr"))
        self.gridLayout_3.addWidget(self.drawArr, 1, 0, 1, 1)
        self.drawRefCents = QtGui.QCheckBox(MagicPlot)
        self.drawRefCents.setObjectName(_fromUtf8("drawRefCents"))
        self.gridLayout_3.addWidget(self.drawRefCents, 0, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_3, 2, 0, 1, 1)

        self.retranslateUi(MagicPlot)
        QtCore.QMetaObject.connectSlotsByName(MagicPlot)

    def retranslateUi(self, MagicPlot):
        MagicPlot.setWindowTitle(_translate("MagicPlot", "Form", None))
        self.getLiveData.setText(_translate("MagicPlot", "Get Live Data", None))
        self.openFitsFile.setText(_translate("MagicPlot", "Open FITS file", None))
        self.plot1dRealtime.setText(_translate("MagicPlot", "1-D Realtime", None))
        self.plotRand2d.setText(_translate("MagicPlot", "2-D Random", None))
        self.bufferSizeSlider.setToolTip(_translate("MagicPlot", "<html><head/><body><p>Set buffer size</p></body></html>", None))
        self.plotSelected.setText(_translate("MagicPlot", "Plot Selected", None))
        self.subApDraw.setText(_translate("MagicPlot", "Draw Subaps", None))
        self.plotRand1d.setText(_translate("MagicPlot", "1-D Random", None))
        self.drawCentroids.setText(_translate("MagicPlot", "Cents", None))
        self.drawArr.setText(_translate("MagicPlot", "Arrows", None))
        self.drawRefCents.setText(_translate("MagicPlot", "Ref Cents", None))

