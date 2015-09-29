from __future__ import division

from PyQt4 import QtCore, QtGui
import transformPlugins

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
        for i in self.tList:
            action = QtGui.QAction(i.name, self)
            action.triggered.connect(lambda: self.aList.append(i))
            self.transMenu.addAction(action)

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


