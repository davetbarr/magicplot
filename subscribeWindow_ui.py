# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ojdf/Documents/MagicPlot/subscribeWindow.ui'
#
# Created: Fri Aug 28 17:26:50 2015
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

class Ui_subscribeWindow(object):
    def setupUi(self, subscribeWindow):
        subscribeWindow.setObjectName(_fromUtf8("subscribeWindow"))
        subscribeWindow.resize(311, 420)
        self.gridLayoutWidget = QtGui.QWidget(subscribeWindow)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 10, 214, 131))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.checkPixels = QtGui.QCheckBox(self.gridLayoutWidget)
        self.checkPixels.setObjectName(_fromUtf8("checkPixels"))
        self.gridLayout.addWidget(self.checkPixels, 1, 0, 1, 1)
        self.checkSubaps = QtGui.QCheckBox(self.gridLayoutWidget)
        self.checkSubaps.setObjectName(_fromUtf8("checkSubaps"))
        self.gridLayout.addWidget(self.checkSubaps, 4, 0, 1, 1)
        self.checkCents = QtGui.QCheckBox(self.gridLayoutWidget)
        self.checkCents.setObjectName(_fromUtf8("checkCents"))
        self.gridLayout.addWidget(self.checkCents, 3, 0, 1, 1)
        self.checkPlotPixels = QtGui.QCheckBox(self.gridLayoutWidget)
        self.checkPlotPixels.setText(_fromUtf8(""))
        self.checkPlotPixels.setObjectName(_fromUtf8("checkPlotPixels"))
        self.gridLayout.addWidget(self.checkPlotPixels, 1, 1, 1, 1)
        self.checkPlotCalPixels = QtGui.QCheckBox(self.gridLayoutWidget)
        self.checkPlotCalPixels.setText(_fromUtf8(""))
        self.checkPlotCalPixels.setObjectName(_fromUtf8("checkPlotCalPixels"))
        self.gridLayout.addWidget(self.checkPlotCalPixels, 2, 1, 1, 1)
        self.checkCalPixels = QtGui.QCheckBox(self.gridLayoutWidget)
        self.checkCalPixels.setObjectName(_fromUtf8("checkCalPixels"))
        self.gridLayout.addWidget(self.checkCalPixels, 2, 0, 1, 1)
        self.checkPlotCents = QtGui.QCheckBox(self.gridLayoutWidget)
        self.checkPlotCents.setText(_fromUtf8(""))
        self.checkPlotCents.setObjectName(_fromUtf8("checkPlotCents"))
        self.gridLayout.addWidget(self.checkPlotCents, 3, 1, 1, 1)
        self.checkPlotSubaps = QtGui.QCheckBox(self.gridLayoutWidget)
        self.checkPlotSubaps.setText(_fromUtf8(""))
        self.checkPlotSubaps.setObjectName(_fromUtf8("checkPlotSubaps"))
        self.gridLayout.addWidget(self.checkPlotSubaps, 4, 1, 1, 1)
        self.label = QtGui.QLabel(self.gridLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.retranslateUi(subscribeWindow)
        QtCore.QMetaObject.connectSlotsByName(subscribeWindow)

    def retranslateUi(self, subscribeWindow):
        subscribeWindow.setWindowTitle(_translate("subscribeWindow", "Form", None))
        self.checkPixels.setText(_translate("subscribeWindow", "Pixels", None))
        self.checkSubaps.setText(_translate("subscribeWindow", "Subaps", None))
        self.checkCents.setText(_translate("subscribeWindow", "Cents", None))
        self.checkCalPixels.setText(_translate("subscribeWindow", "CalPixels", None))
        self.label.setText(_translate("subscribeWindow", "Plot", None))
        self.label_2.setText(_translate("subscribeWindow", "Subscribe to:", None))

