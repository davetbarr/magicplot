"""
A class to draw shapes onto a QGraphicsView
"""
import os
SRC_PATH = os.path.dirname(os.path.abspath(__file__))
os.system("pyuic4 {0}/shapeDrawer.ui > {0}/shapeDrawer_ui.py".format(SRC_PATH))
import shapeDrawer_ui

from PyQt4 import QtCore, QtGui
import shapeHolder

class ShapeDrawer(QtGui.QWidget, shapeDrawer_ui.Ui_ShapeDrawer):

    """
    A Widget providing a list of shapes which can be drawn onto
    a QGraphicsView. The shapes are then added to a list and can
    be later removed or edited.

    Parameters:
        view (QGraphicsView): The Graphics View to draw onto
    """

    def __init__(self, view=None, item=None):
        # Run init on th e QWidget class
        super(ShapeDrawer, self).__init__()
        self.setupUi(self)

        # Drawing buttons
        self.drawRectButton.clicked.connect(self.drawRect)
        self.drawLineButton.clicked.connect(self.drawLine)
        self.drawGridButton.clicked.connect(self.drawGrid)

        # Setup list to hold shapes
        self.shapes = shapeHolder.ShapeContainer()
        self.shapeList = ShapeList(self)
        self.verticalLayout.addWidget(self.shapeList)
        self.shapeList.setModel(self.shapes)
        self.index = 0
        self.isDrawingRect = 0
        self.isDrawingLine = 0


        # Connect double click to delete shape
        self.shapeList.doubleClicked.connect(self.openDialog)
        self.shapeList.delKeySig.connect(self.shapes.removeShape)

        self.setView(view, item)

    def getShapes(self):
        return self.shapes

    def setView(self, view, item):
        self.plotView = view
        self.plotItem = item
        try:
            self.viewBox = self.plotView.getViewBox()
        except AttributeError:
            pass
        self.clearShapes()
        # Get the scene object from the view.
        # pyqtgraph imageView is inconsistant, hence try/except
        if view!=None:
            try:
                self.scene = self.plotView.scene()
                self.scene.sigMouseClicked.connect(self.shapeCheck)
            except TypeError:
                self.scene = self.plotView.scene
                self.scene.sigMouseClicked.connect(self.shapeCheck)

    def clearShapes(self):
        self.shapes.clearShapes()

############ Dialog methods

    def openDialog(self, index):
        shape = self.shapes[index.row()]
        if type(shape)==Grid:
            self.dialog = GridDialog(shape=shape)
            self.dialog.applySig.connect(self.applyGridChanges)
            self.dialog.accepted.connect(self.applyGridChanges)
        elif type(shape)==QtGui.QGraphicsRectItem:
            self.dialog = RectDialog(shape=shape)
            self.dialog.applySig.connect(self.applyRectChanges)
            self.dialog.accepted.connect(self.applyRectChanges)
        elif type(shape)==QtGui.QGraphicsLineItem:
            self.dialog = LineDialog(shape)
            self.dialog.applySig.connect(self.applyLineChanges)
            self.dialog.accepted.connect(self.applyLineChanges)

    def applyGridChanges(self):
        print "apply"
        xPos, yPos, xSize, ySize, rows, columns, color, result = \
            self.dialog.getValues()
        self.dialog.shape.nRows = rows
        self.dialog.shape.nColumns = columns
        self.dialog.shape.color = color
        self.dialog.shape.setRect(QtCore.QRectF(xPos,yPos, xSize, ySize))
        self.dialog.shape.update()

    def applyRectChanges(self):
        print "apply"
        x, y, xSize, ySize, color, result = self.dialog.getValues()
        self.dialog.shape.setRect(x, y, xSize, ySize)
        self.dialog.shape.setPen(QtGui.QPen(color))

    def applyLineChanges(self):
        print "apply"
        x1, y1, x2, y2, color, result = self.dialog.getValues()
        self.dialog.shape.setLine(x1, y1, x2, y2)
        self.dialog.shape.setPen(QtGui.QPen(color))

# Rectangle drawing methods
#############################

    def drawRect(self):
        # if size is 0, draw shape, else add shape
        x, y, xSize, ySize, color, accepted = \
            RectDialog(modal=True).getValues()
        if (xSize and ySize) == 0.0 and accepted == 1:
            self.color = color
            self.scene.sigMouseClicked.connect(self.mouseClicked_rect1)
            print("DRAW RECT!")
        elif accepted == 1:
            self.shapes.append(QtGui.QGraphicsRectItem(
                    QtCore.QRectF(x,y,xSize,ySize)))
            self.shapes[-1].setPen(QtGui.QPen(color))
            self.plotView.addItem(self.shapes[-1])


    def updateRect(self, x, y, xSize, ySize):
        self.shapes[-1].setRect(QtCore.QRectF(x, y, xSize, ySize))

    def mouseMoved_rect(self, pos):
        '''
        method attached to pyqtgraph image widget which gets the mouse position
        If the mouse is in the image, print both the mouse position and
        pixel value to the gui
        '''

        imgPos = self.viewBox.mapSceneToView(pos)
        scene = self.scene
        # Only update when mouse is in image
        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < scene.height
                and pos.x() < scene.width):


            self.mousePos = (imgPos.x(), imgPos.y())

            xSize = self.mousePos[0] - self.rectStartPos[0]
            ySize = self.mousePos[1] - self.rectStartPos[1]

            # xSize = pos.x() - self.rectStartPos[0]
            # ySize = pos.y() - self.rectStartPos[1]
            self.updateRect(
                    self.rectStartPos[0], self.rectStartPos[1],
                    xSize, ySize)

    def mouseClicked_rect1(self, event):
        print("Mouse clicked 1!")
        pos = event.scenePos()
        print(pos)
        scene = self.scene
        imgPos = self.viewBox.mapSceneToView(pos)
        print imgPos
        #self.isDrawingRect =1
        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < scene.height
                and pos.x() < scene.width):

            self.rectStartPos = (imgPos.x(), imgPos.y())
            self.shapes.append(QtGui.QGraphicsRectItem(
                    QtCore.QRectF(imgPos.x(),imgPos.y(),0,0)))
            self.shapes[-1].setPen(QtGui.QPen(self.color))
            self.shapes[-1].setZValue(100)
            #self.shapes[-1].setBrush(QtGui.QBrush(QtCore.Qt.red))


            self.plotView.addItem(self.shapes[-1])
            self.updateRect(imgPos.x(), imgPos.y(), 0,0)
            #self.updateRect(pos.x(), pos.y(), 0 ,0)
            self.scene.sigMouseMoved.connect(
                    self.mouseMoved_rect)
            self.scene.sigMouseClicked.disconnect(
                    self.mouseClicked_rect1)
            self.scene.sigMouseClicked.connect(
                    self.mouseClicked_rect2)

    def mouseClicked_rect2(self, event):
        print("Mouse clicked 2")
        pos = event.pos()
        scene = self.scene
        #imgPos = self.plotItem.mapFromScene(pos)
        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < scene.height
                and pos.x() < scene.width):

            self.scene.sigMouseMoved.disconnect(
                    self.mouseMoved_rect)
            self.scene.sigMouseClicked.disconnect(
                    self.mouseClicked_rect2)

            self.shapes.updateView()
        self.isDrawingRect = 0

    def drawRectFromRect(self, rect):
        #self.shapes.append(QtGui.QGraphicsRectItem(rect))
        #self.shapes[-1].setPen(QtGui.QPen(QtCore.Qt.blue))
        self.plotView.addItem(rect)

# Line drawing methods
#############################
    def drawLine(self):
        # if all values 0 , draw shape, otherwise add shape
        x1, y1, x2, y2, color, accepted = \
            LineDialog(modal=True).getValues()
        print color
        if (x1 - x2 and y1 - y2) == 0.0 and accepted == 1:
            self.color = color
            self.scene.sigMouseClicked.connect(self.mouseClicked_line1)
            print("DRAW LINE!")
        elif accepted == 1:
            self.shapes.append(QtGui.QGraphicsLineItem(
                    x1, y1, x2, y2))
            self.shapes[-1].setPen(QtGui.QPen(color))
            self.plotView.addItem(self.shapes[-1])


    def updateLine(self, x1, x2, y1, y2):
        self.shapes[-1].setLine(QtCore.QLineF(x1, x2, y1, y2))

    def mouseMoved_line(self, pos):
        '''
        method attached to pyqtgraph image widget which gets the mouse position
        If the mouse is in the image, print both the mouse position and
        pixel value to the gui
        '''

        imgPos = self.viewBox.mapSceneToView(pos)

        # Only update when mouse is in image
        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < self.scene.height
                and pos.x() < self.scene.width):

            self.mousePos = (imgPos.x(), imgPos.y())

            xSize = self.mousePos[0] - self.lineStartPos[0]
            ySize = self.mousePos[1] - self.lineStartPos[1]
            self.updateLine(
                    self.lineStartPos[0], self.lineStartPos[1],
                    self.mousePos[0], self.mousePos[1])

    def mouseClicked_line1(self, event):
        print("Line Mouse clicked 1!")
        pos = event.scenePos()
        imgPos = self.viewBox.mapSceneToView(pos)
        self.isDrawingLine = 1
        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < self.scene.height
                and pos.x() < self.scene.width):

            self.lineStartPos = (imgPos.x(), imgPos.y())

            self.shapes.append(
                    QtGui.QGraphicsLineItem(QtCore.QLineF(
                            imgPos.x(),imgPos.y(),imgPos.x(),imgPos.y())))
            self.plotView.addItem(self.shapes[-1])
            self.shapes[-1].setPen(QtGui.QPen(self.color))

            #self.shapes[-1].setZValue(100)

            #imgPos = self.plotItem.mapFromScene(pos)

            self.updateLine(imgPos.x(), imgPos.y(), imgPos.x(),imgPos.y())
            self.scene.sigMouseMoved.connect(
                    self.mouseMoved_line)
            self.scene.sigMouseClicked.disconnect(
                    self.mouseClicked_line1)
            self.scene.sigMouseClicked.connect(
                    self.mouseClicked_line2)

    def mouseClicked_line2(self, event):
        print("Line Mouse clicked 2")
        pos = event.scenePos()
        imgPos = self.viewBox.mapSceneToView(pos)
        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < self.scene.height
                and pos.x() < self.scene.width):
            self.scene.sigMouseMoved.disconnect(
                    self.mouseMoved_line)
            self.scene.sigMouseClicked.disconnect(
                    self.mouseClicked_line2)

            self.shapes.updateView()
        self.isDrawingLine = 0

########## Grid Drawing ##############
    # if size is 0, draw grid, else add grid
    def drawGrid(self):
        xPos, yPos, xSize, ySize, rows, cols, color, accepted = \
            GridDialog(modal=True).getValues()
        if (xSize and ySize) == 0 and accepted == 1:
            self.rows, self.cols, self.color = rows, cols, color
            self.scene.sigMouseClicked.connect(self.mouseClicked_grid1)
        elif accepted == 1:
            grid = Grid(QtCore.QRectF(
                xPos, yPos, xSize, ySize), rows, cols)
            self.shapes.append(grid)
            grid.color = color
            self.plotView.addItem(grid)

    def updateGrid(self, x, y, xSize, ySize):
        self.shapes[-1].setRect(QtCore.QRectF(x, y, xSize, ySize))

    def mouseMoved_grid(self, pos):
        imgPos = self.viewBox.mapSceneToView(pos)
        scene = self.scene
        # Only update when mouse is in image
        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < scene.height
                and pos.x() < scene.width):


            self.mousePos = (imgPos.x(), imgPos.y())

            xSize = self.mousePos[0] - self.gridStartPos[0]
            ySize = self.mousePos[1] - self.gridStartPos[1]

            # xSize = pos.x() - self.rectStartPos[0]
            # ySize = pos.y() - self.rectStartPos[1]
            self.updateGrid(
                    self.gridStartPos[0], self.gridStartPos[1],
                    xSize, ySize)

    def mouseClicked_grid1(self, event):
        print("Grid Mouse clicked 1")
        pos = event.scenePos()
        print(pos)
        scene = self.scene
        imgPos = self.viewBox.mapSceneToView(pos)
        print imgPos
        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < scene.height
                and pos.x() < scene.width):

            self.gridStartPos = (imgPos.x(), imgPos.y())
            self.grid = Grid(QtCore.QRectF(
                imgPos.x(),imgPos.y(),0,0),self.rows,self.cols)
            self.shapes.append(self.grid)
            # self.shapes[-1].setPen(QtGui.QPen(QtCore.Qt.red))
            # self.shapes[-1].setZValue(100)
            #self.shapes[-1].setBrush(QtGui.QBrush(QtCore.Qt.red))
            self.updateGrid(imgPos.x(), imgPos.y(), 0,0)
            self.grid.color = self.color
            # gridShapes = self.grid.getShapes()
            # for i in gridShapes:
            #     self.plotView.addItem(i)
            #     i.setPen(QtGui.QPen(QtCore.Qt.red))
            self.plotView.addItem(self.grid)
            # self.grid.setPen(QtGui.QPen(self.color))
            self.scene.sigMouseMoved.connect(
                    self.mouseMoved_grid)
            self.scene.sigMouseClicked.disconnect(
                    self.mouseClicked_grid1)
            self.scene.sigMouseClicked.connect(
                    self.mouseClicked_grid2)

    def mouseClicked_grid2(self, event):
        print("Mouse clicked 2")
        pos = event.pos()
        scene = self.scene
        #imgPos = self.plotItem.mapFromScene(pos)
        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < scene.height
                and pos.x() < scene.width):

            self.scene.sigMouseMoved.disconnect(
                    self.mouseMoved_grid)
            self.scene.sigMouseClicked.disconnect(
                    self.mouseClicked_grid2)

            self.shapes.updateView()

    def shapeCheck(self, event):
        pass
    #     pos = event.pos()
    #     imgPos = self.plotItem.mapFromScene(pos)
    #     index = 0
    #     if self.isDrawingRect or self.isDrawingLine:
    #         print "drawing, not registered click"
    #         return None
    #     for i in self.shapes:
    #         if i.contains(imgPos):
    #             print index
    #             self.index = index
    #             self.changeShapeSignal.emit()
    #             #this is really bad, must be better way
    #             break
    #         else:
    #             index += 1

class ShapeDialog(QtGui.QDialog):

    applySig = QtCore.pyqtSignal()

    def __init__(self, shape=None, parent=None, modal=False):
        super(ShapeDialog, self).__init__(parent)
        self.layout = QtGui.QGridLayout(self)
        self.colorButton = QtGui.QPushButton("Color")
        self.applyButton = QtGui.QPushButton("Apply")
        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
            | QtGui.QDialogButtonBox.Apply,
            QtCore.Qt.Horizontal, self)
        # get apply button and connect to apply slot
        applyButton = self.buttons.buttons()[2]
        applyButton.clicked.connect(self.apply)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.colorButton.clicked.connect(self.getColor)
        self.shape = shape
        if self.shape == None:
            applyButton.setEnabled(False)
            self.color = QtGui.QColor("red") #defualt
        else:
            self.color = self.shape.pen().color()
        # if init with shape, set values in dialog from shape (see subclasses)
        self.setupUi()
        self.setValuesFromShape()
        if modal:
            self.exec_()
        else:
            self.show()

    def getColor(self):
        colorDialog = QtGui.QColorDialog(self.color)
        newColor = colorDialog.getColor()
        if newColor.isValid():
            self.color = newColor

    def apply(self):
        print "emit"
        self.applySig.emit()

    def setValuesFromShape(self):
        pass

    def setupUi(self):
        pass

class RectDialog(ShapeDialog):

    def __init__(self, shape=None, parent=None, modal=False):
        super(RectDialog, self).__init__(shape=shape, parent=parent,
                                         modal=modal)

    def setupUi(self):
        self.posLabel = QtGui.QLabel("Pos (x,y)")
        self.xPosBox = QtGui.QDoubleSpinBox()
        self.xPosBox.setMinimum(-99.99)
        self.yPosBox = QtGui.QDoubleSpinBox()
        self.yPosBox.setMinimum(-99.99)
        self.sizeLabel = QtGui.QLabel("Size (width, height)")
        self.xSizeBox = QtGui.QDoubleSpinBox()
        self.xSizeBox.setMinimum(-99.99)
        self.ySizeBox = QtGui.QDoubleSpinBox()
        self.ySizeBox.setMinimum(-99.99)

        self.layout.addWidget(self.posLabel)
        self.layout.addWidget(self.xPosBox)
        self.layout.addWidget(self.yPosBox)
        self.layout.addWidget(self.sizeLabel)
        self.layout.addWidget(self.xSizeBox)
        self.layout.addWidget(self.ySizeBox)

        self.layout.addWidget(self.colorButton)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def setValuesFromShape(self):
        try:
            rect = self.shape.rect()
            x, y = rect.x(), rect.y()
            sizeX, sizeY = rect.width(), rect.height()
            self.xPosBox.setValue(x)
            self.yPosBox.setValue(y)
            self.xSizeBox.setValue(sizeX)
            self.ySizeBox.setValue(sizeY)
        except AttributeError as e:
            print "no shape"

    def getValues(self):
        return (self.xPosBox.value(),
                self.yPosBox.value(),
                self.xSizeBox.value(),
                self.ySizeBox.value(),
                self.color,
                self.result())


class LineDialog(ShapeDialog):

    def __init__(self, shape=None, parent=None, modal=False):
        super(LineDialog, self).__init__(shape=shape, parent=parent,
                                         modal=modal)

    def setupUi(self):
        self.startLabel = QtGui.QLabel("Start Point")
        self.x1Box = QtGui.QDoubleSpinBox()
        self.x1Box.setMinimum(-99.99)
        self.y1Box = QtGui.QDoubleSpinBox()
        self.y1Box.setMinimum(-99.99)
        self.endLabel = QtGui.QLabel("End Point")
        self.x2Box = QtGui.QDoubleSpinBox()
        self.x2Box.setMinimum(-99.99)
        self.y2Box = QtGui.QDoubleSpinBox()
        self.y2Box.setMinimum(-99.99)
        self.layout.addWidget(self.startLabel)
        self.layout.addWidget(self.x1Box)
        self.layout.addWidget(self.y1Box)
        self.layout.addWidget(self.endLabel)
        self.layout.addWidget(self.x2Box)
        self.layout.addWidget(self.y2Box)

        self.layout.addWidget(self.colorButton)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def setValuesFromShape(self):
        try:
            line = self.shape.line()
            self.x1Box.setValue(line.x1())
            self.y1Box.setValue(line.y1())
            self.x2Box.setValue(line.x2())
            self.y2Box.setValue(line.y2())
        except AttributeError:
            pass

    def getValues(self):
        return (self.x1Box.value(),
                self.y1Box.value(),
                self.x2Box.value(),
                self.y2Box.value(),
                self.color,
                self.result())

class GridDialog(ShapeDialog):

    def __init__(self, shape=None, parent=None, modal=False):
        super(GridDialog, self).__init__(shape=shape, parent=parent,
                                         modal=modal)

    def setupUi(self):
        self.posLabel = QtGui.QLabel("Pos (x,y)")
        self.xPosBox = QtGui.QDoubleSpinBox()
        self.xPosBox.setMinimum(-99.99)
        self.yPosBox = QtGui.QDoubleSpinBox()
        self.yPosBox.setMinimum(-99.99)
        self.sizeLabel = QtGui.QLabel("Size (width, height)")
        self.xSizeBox = QtGui.QDoubleSpinBox()
        self.xSizeBox.setMinimum(-99.99)
        self.ySizeBox = QtGui.QDoubleSpinBox()
        self.ySizeBox.setMinimum(-99.99)
        self.layout.addWidget(self.posLabel)
        self.layout.addWidget(self.xPosBox)
        self.layout.addWidget(self.yPosBox)
        self.layout.addWidget(self.sizeLabel)
        self.layout.addWidget(self.xSizeBox)
        self.layout.addWidget(self.ySizeBox)

        self.rowsLabel = QtGui.QLabel("# Rows")
        self.rowsBox = QtGui.QSpinBox()
        self.columnsLabel = QtGui.QLabel("# Columns")
        self.columnsBox = QtGui.QSpinBox()
        self.layout.addWidget(self.rowsLabel)
        self.layout.addWidget(self.rowsBox)
        self.layout.addWidget(self.columnsLabel)
        self.layout.addWidget(self.columnsBox)

        self.layout.addWidget(self.colorButton)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def getValues(self):
        return (self.xPosBox.value(),
                self.yPosBox.value(),
                self.xSizeBox.value(),
                self.ySizeBox.value(),
                self.rowsBox.value(),
                self.columnsBox.value(),
                self.color,
                self.result()
                )

    def setValuesFromShape(self):
        try:
            self.xPosBox.setValue(self.shape.outRect.rect().x())
            self.yPosBox.setValue(self.shape.outRect.rect().y())
            self.xSizeBox.setValue(self.shape.outRect.rect().width())
            self.ySizeBox.setValue(self.shape.outRect.rect().height())
            self.rowsBox.setValue(self.shape.nRows)
            self.columnsBox.setValue(self.shape.nColumns)
        except AttributeError:
            pass


class Grid(QtGui.QGraphicsRectItem):

    def __init__(self, rect, nRows, nColumns):
        super(Grid, self).__init__()
        self.outRect = QtGui.QGraphicsRectItem(rect, self)
        self.nRows = nRows
        self.nColumns = nColumns
        self.color = QtGui.QColor("red")
        self.update()

    def setRect(self, rect):
        self.outRect.setRect(rect)
        self.update()

    def update(self):
        self.vSpacing = self.outRect.rect().height() / self.nRows
        self.hSpacing = self.outRect.rect().width() / self.nColumns
        for i, line in enumerate(self.hLines):
            x1 = self.outRect.rect().left()
            y1 = self.outRect.rect().top() + (i+1)*self.vSpacing
            x2 = self.outRect.rect().right()
            y2 = y1
            line.setLine(x1, y1, x2, y2)
        for j, line in enumerate(self.vLines):
            x1 = self.outRect.rect().left() + (j+1)*self.hSpacing
            y1 = self.outRect.rect().top()
            x2 = x1
            y2 = self.outRect.rect().bottom()
            line.setLine(x1, y1, x2, y2)
        self.color = self._color

    @property
    def shapes(self):
        return [self.outRect] + self.hLines + self.vLines

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
        self._pen = QtGui.QPen(color)
        self.outRect.setPen(self._pen)
        for i in self.vLines + self.hLines:
            i.setPen(QtGui.QPen(color))

    def pen(self):
        return self._pen

    @property
    def nRows(self):
        return self._nRows

    @nRows.setter
    def nRows(self, nRows):
        self._nRows = nRows
        try:
            for i in self.hLines:
                i.setVisible(False)
        except AttributeError:
            pass
        self.hLines = []
        self.hLines = [QtGui.QGraphicsLineItem(self) for i in range(nRows-1)]

    @property
    def nColumns(self):
        return self._nColumns

    @nColumns.setter
    def nColumns(self, nColumns):
        self._nColumns = nColumns
        try:
            for i in self.vLines:
                i.setVisible(False)
        except AttributeError:
            pass
        self.vLines = []
        self.vLines = [QtGui.QGraphicsLineItem(self) for i in range(nColumns-1)]

class ShapeList(QtGui.QListView):
    """
    QListView to view shapes drawn on MagicPlot, reimplemented keyPressEvent
    to handle delete key (n.b. this breaks the arrow keys)
    """
    delKeySig = QtCore.pyqtSignal(object)

    def __init__(self, parent):
        super(ShapeList, self).__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.delKeySig.emit(self.currentIndex())
        else:
            pass
