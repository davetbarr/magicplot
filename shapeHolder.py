from PyQt4 import QtCore, QtGui
from shapeDrawer import Grid


class ShapeContainer(QtCore.QAbstractListModel):


    def __init__(self):
        super(ShapeContainer, self).__init__()

        self.shapeList = []

    def rowCount(self, index):
        return len(self.shapeList)

    def data(self, index, role):
        if role!=QtCore.Qt.DisplayRole:
            return None

        if len(self.shapeList)==0:
            return None

        return getShapeName(self.shapeList[index.row()])


    def append(self, shape):

        self.beginInsertRows(QtCore.QModelIndex(), 0, 0)
        self.shapeList.append(shape)
        self.endInsertRows()

    def removeShape(self, index):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, 0)
        shape = self.shapeList.pop(index.row())
        shape.setVisible(False)
        self.endRemoveRows()

    def clearShapes(self):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, 0)
        for i in self.shapeList:
            i.setVisible(False)
        self.shapeList = []
        self.endRemoveRows()

    def updateView(self):
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def __getitem__(self, index):
        return self.shapeList[index]

def getShapeName(shape):
    """
    Helper function to provide a description of a Qt QGraphics shape

    Parameters:
        shape (QtGui.QGraphics shape): The shape to describe

    Returns
        str: A name describing that shape
    """

    if type(shape)==QtGui.QGraphicsRectItem:
        r = shape.rect()
        return "Rectangle @ ({:.1f}, {:.1f}), size: ({:.1f}, {:.1f})".format(
                r.x(), r.y(), r.width(), r.height()
                )
    elif type(shape)==QtGui.QGraphicsLineItem:
        l = shape.line()
        return "Line @ ({:.1f}, {:.1f}) to ({:.1f}, {:.1f})".format(
                l.x1(), l.y1(), l.x2(), l.y2()
                )
    elif type(shape)==Grid:
        r = shape.outRect.rect()
        nRows = shape.nRows
        nColumns = shape.nColumns
        return "Grid @ ({:.1f}, {:.1f}), Rows: {:d}, Columns: {:d}".format(
                r.x(), r.y(), nRows, nColumns
                )
    else:
        return "Unkown Shape"
