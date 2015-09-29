from __future__ import division

from PyQt4 import QtCore, QtGui
import transformPlugins

import copy

class Transformer(QtCore.QObject):
    sigActiveToggle = QtCore.pyqtSignal(bool)
    def __init__(self):
        super(Transformer, self).__init__()
        self.tList = transformPlugins.TransformList(None)
        self.tList.getTransforms()
        self.aList = transformPlugins.TransformList(self.tList)
        self.active = False
        self.initContextMenu()

    def initContextMenu(self):
        self.transMenu = QtGui.QMenu('Transforms')       
        runTransforms = QtGui.QAction('Activate Transforms', self)
        runTransforms.setCheckable(True)
        runTransforms.toggled.connect(self.toggleRunning)
        self.transMenu.addAction(runTransforms)
        openDialog = QtGui.QAction('Open Transforms dialog', self)
        openDialog.triggered.connect(self.openDialog)
        self.transMenu.addAction(openDialog)
        self.transMenu.addSeparator()
        self.quickTransforms = QtGui.QActionGroup(self)
        for row, plugin in enumerate(self.tList):
            action = QtGui.QAction(plugin.name, self.quickTransforms)
            action.setData(row)
            self.transMenu.addAction(action)
        self.quickTransforms.triggered.connect(self.addFromContextMenu)

    def addFromContextMenu(self, action):
        if action.data() is not None:
            row = action.data().toInt()[0]
            print row
            self.aList.append(self.tList[row])
        else:
            pass
        

    def transform(self, data):
        if self.active:
            for i in self.aList:
                i.setData(data)
                data = i.run()
            return data
        else:
            return data
    
    def openDialog(self):
        self.dialog = transformPlugins.TransformDialog(tList=self.tList,
                aList=self.aList)
        self.dialog.show()
        
    def toggleRunning(self, checked):
        self.active = checked
        self.sigActiveToggle.emit(checked)


