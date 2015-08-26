# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ojdf/Documents/MagicPlot/shapeDrawer.ui'
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

class Ui_ShapeDrawer(object):
    def setupUi(self, ShapeDrawer):
        ShapeDrawer.setObjectName(_fromUtf8("ShapeDrawer"))
        ShapeDrawer.resize(128, 317)
        self.gridLayout = QtGui.QGridLayout(ShapeDrawer)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.drawRectButton = QtGui.QPushButton(ShapeDrawer)
        self.drawRectButton.setObjectName(_fromUtf8("drawRectButton"))
        self.verticalLayout.addWidget(self.drawRectButton)
        self.drawLineButton = QtGui.QPushButton(ShapeDrawer)
        self.drawLineButton.setObjectName(_fromUtf8("drawLineButton"))
        self.verticalLayout.addWidget(self.drawLineButton)
        self.shapeList = QtGui.QListView(ShapeDrawer)
        self.shapeList.setObjectName(_fromUtf8("shapeList"))
        self.verticalLayout.addWidget(self.shapeList)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(ShapeDrawer)
        QtCore.QMetaObject.connectSlotsByName(ShapeDrawer)

    def retranslateUi(self, ShapeDrawer):
        ShapeDrawer.setWindowTitle(_translate("ShapeDrawer", "Form", None))
        self.drawRectButton.setText(_translate("ShapeDrawer", "Rectangle", None))
        self.drawLineButton.setText(_translate("ShapeDrawer", "Line", None))

