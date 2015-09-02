from PyQt4 import QtCore, QtGui


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
        g = shape.gridInfo()
        return "Grid @ **gridInfo here**"
    else:
        return "Unkown Shape"

class Grid(object):

    def __init__(self, rect, nRows, nColumns):
        self.rect = QtGui.QGraphicsRectItem(rect)
        self.nRows = nRows
        self.nColumns = nColumns
        self.hLines = [QtGui.QGraphicsLineItem() for i in range(nRows)]
        self.vLines = [QtGui.QGraphicsLineItem() for i in range(nColumns)]

    def setRect(self, rect):
        self.rect.setRect(rect)
        self.update()

    def update(self):
        self.vSpacing = self.rect.rect().height() / self.nRows
        self.hSpacing = self.rect.rect().width() / self.nColumns
        for i, line in enumerate(self.hLines):
            x1 = self.rect.rect().left()
            y1 = self.rect.rect().top() + (i+1)*self.vSpacing
            x2 = self.rect.rect().right()
            y2 = y1
            line.setLine(x1, y1, x2, y2)
        for j, line in enumerate(self.vLines):
            x1 = self.rect.rect().left() + (j+1)*self.hSpacing
            y1 = self.rect.rect().top()
            x2 = x1
            y2 = self.rect.rect().bottom()
            line.setLine(x1, y1, x2, y2)

    def getShapes(self):
        shapeList = [self.rect] + self.hLines + self.vLines
        return shapeList

    def gridInfo(self):
        pass
