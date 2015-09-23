import sys
from PyQt4 import QtGui, QtCore
import numpy
import os
import pickle
import cPickle
PATH = os.path.dirname(os.path.abspath(__file__))

class TransformPlugin():
    """
    Base class for transform plugins for MagicPlot
    """
    def __init__(self, params={}, name='Plugin'):
        self.params = params
        self.name = name

    def setData(self, data):
        self.data = data

    def setParams(self, params):
        self.params = params

    def run(self):
        pass
    
class TransformDialog(QtGui.QDialog):
    """
    Dialog that shows available transforms in a QListView

    Transforms can be applied to data in any order
    """

    def __init__(self, tList=None, aList=None):
        super(TransformDialog, self).__init__()
        self.setupUi(tList, aList)

    def setupUi(self, tList, aList):
        self.layout = QtGui.QGridLayout()
        self.tView = TransformListView()
        self.tView.setModel(tList)
        self.activeView = ActiveTransformListView()
        self.activeView.setModel(aList)
        self.layout.addWidget(self.tView, 0,0)
        self.layout.addWidget(self.activeView, 0,1)
        self.setLayout(self.layout)

class TransformListView(QtGui.QListView):
    """
    List view showing transforms, can be dragged and dropped to active
    transform ListView
    """
    def __init__(self, parent=None):
        super(TransformListView, self).__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-Plugin"):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def startDrag(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return

        selected = self.model().data(index,QtCore.Qt.UserRole)

        bstream = cPickle.dumps(selected)
        mimeData = QtCore.QMimeData()
        mimeData.setData("application/x-Plugin", bstream)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)

        result = drag.start(QtCore.Qt.MoveAction)

    def mouseMoveEvent(self, event):
        self.startDrag(event)

class ActiveTransformListView(QtGui.QListView):
    """
    List view showing active transforms
    """
    def __init__(self, parent=None):
        super(ActiveTransformListView, self).__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-Plugin"):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-Plugin"):
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        data = event.mimeData()
        bstream = data.retrieveData("application/x-Plugin",
                QtCore.QVariant.ByteArray)
        selected = pickle.loads(bstream.toByteArray())
        index = self.indexAt(event.pos())
        row =index.row()
        if row == -1:
            self.model().append(selected)
        else:
            self.model().insertRows(row, 1, plugin=selected)
        
        event.accept()

class TransformList(QtCore.QAbstractListModel):
    """
    Model for TransformListView
    """
    def __init__(self, parent):
        super(TransformList, self).__init__(parent)
        self.parent = parent
        self.tList = []

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid(): return 0
        return len(self.tList)

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsSelectable| \
                    QtCore.Qt.ItemIsDragEnabled| \
                    QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsDragEnabled| \
                QtCore.Qt.ItemIsDropEnabled|QtCore.Qt.ItemIsEnabled

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid(): return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole: return self.tList[index.row()].name
        elif role == QtCore.Qt.UserRole:
            plugin = self.tList[index.row()]
            return plugin
        return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid() or role!=QtCore.Qt.DisplayRole: return False
        
        self.tList[index.row()]=value.name
        self.dataChanged.emit(index,index)
        return True

    def append(self, transform):
        self.beginInsertRows(QtCore.QModelIndex(), 0, 0)
        self.tList.append(transform)
        self.endInsertRows()

    def insertRows(self, row, count, parent=QtCore.QModelIndex(), plugin=None):
        if parent.isValid(): return False

        beginRow=max(0,row)
        endRow=min(row+count-1,len(self.tList))

        self.beginInsertRows(parent, beginRow, endRow)

        for i in xrange(beginRow, endRow+1): self.tList.insert(i,plugin) 

        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        if parent.isValid(): return False
        if row >= len(self.tList) or row+count <=0: return False

        beginRow = max(0,row)
        endRow = min(row+(count-1), len(self.tList)-1)

        self.beginRemoveRows(parent, beginRow, endRow)

        for i in xrange(beginRow, endRow+1): self.tList.pop(i)

        self.endRemoveRows()
        return True

    def __getitem__(self, index):
        return self.tList[index]

    def getTransforms(self):
        path = os.path.abspath(os.path.join(PATH, '../plugins/transforms'))
        for i in os.listdir(path):
            fname = os.path.join(path, i)
            with open(fname, 'r') as f:
                exec(f, globals())
                self.append(Plugin())

if __name__ == '__main__':
    app = QtGui.QApplication([])
    tList = TransformList(None)
    tList.append(TransformPlugin(name='this'))
    tList.append(TransformPlugin(name='and this'))
    tList.getTransforms()
    aList = TransformList(None)
    Dialog = TransformDialog(tList=tList, aList=aList)
    Dialog.show()
    try:
        __IPYTHON__
    except NameError:
        __IPYTHON__=False

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        if not __IPYTHON__:
            QtGui.QApplication.instance().exec_()
    








