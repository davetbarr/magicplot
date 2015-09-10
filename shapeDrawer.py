"""
A class to draw shapes onto a QGraphicsView
"""
import os
SRC_PATH = os.path.dirname(os.path.abspath(__file__))
os.system("pyuic4 {0}/shapeDrawer.ui > {0}/shapeDrawer_ui.py".format(SRC_PATH))
import shapeDrawer_ui

from PyQt4 import QtCore, QtGui
import shapeHolder
import numpy

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
        self.drawCircleButton.clicked.connect(self.drawCirc)

        # Setup list to hold shapes
        self.shapes = shapeHolder.ShapeContainer(self)
        self.shapeList = ShapeList(self)
        self.verticalLayout.addWidget(self.shapeList)
        self.shapeList.setModel(self.shapes)


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
        elif type(shape)==QtGui.QGraphicsEllipseItem:
            self.dialog = CircDialog(shape)
            self.dialog.applySig.connect(self.applyCircChanges)
            self.dialog.accepted.connect(self.applyCircChanges)

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

    def applyCircChanges(self):
        print "apply"
        xPos, yPos, r, color, result = self.dialog.getValues()
        self.dialog.shape.setRect(xPos-r, yPos-r, 2*r, 2*r)
        self.dialog.shape.setPen(QtGui.QPen(color))

# Rectangle drawing methods
#############################

    def drawRect(self):
        self.dialog = RectDialog()
        self.scene.sigMouseClicked.connect(self.mouseClicked_rect1)
        self.dialog.accepted.connect(self.drawRectFromValues)
        self.dialog.rejected.connect(self.cancelDrawRect)

    def cancelDrawRect(self):
        self.scene.sigMouseClicked.disconnect(self.mouseClicked_rect1)

    def drawRectFromValues(self):
        x, y, xSize, ySize, color, accepted = self.dialog.getValues()
        self.shapes.append(QtGui.QGraphicsRectItem(
                QtCore.QRectF(x,y,xSize,ySize)))
        self.shapes[-1].setPen(QtGui.QPen(color))
        self.plotView.addItem(self.shapes[-1])

    def updateRect(self, x, y, xSize, ySize):
        self.shapes[-1].setRect(QtCore.QRectF(x, y, xSize, ySize))
        self.dialog.setValuesFromShape()

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
        self.dialog.accepted.disconnect(self.drawRectFromValues)
        self.dialog.accepted.connect(self.applyRectChanges)
        self.dialog.applySig.connect(self.applyRectChanges)
        pos = event.scenePos()
        print(pos)
        scene = self.scene
        imgPos = self.viewBox.mapSceneToView(pos)
        print imgPos
        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < scene.height
                and pos.x() < scene.width):

            self.rectStartPos = (imgPos.x(), imgPos.y())
            self.shapes.append(QtGui.QGraphicsRectItem(
                    QtCore.QRectF(imgPos.x(),imgPos.y(),0,0)))
            self.shapes[-1].setPen(QtGui.QPen(self.dialog.color))
            self.shapes[-1].setZValue(100)
            #self.shapes[-1].setBrush(QtGui.QBrush(QtCore.Qt.red))


            self.plotView.addItem(self.shapes[-1])
            self.dialog.setShape(self.shapes[-1])
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

    def drawRectFromRect(self, rect):
        #self.shapes.append(QtGui.QGraphicsRectItem(rect))
        #self.shapes[-1].setPen(QtGui.QPen(QtCore.Qt.blue))
        self.plotView.addItem(rect)

# Line drawing methods
#############################
    def drawLine(self):
        self.dialog = LineDialog()
        self.scene.sigMouseClicked.connect(self.mouseClicked_line1)
        self.dialog.accepted.connect(self.drawLineFromValues)
        self.dialog.rejected.connect(self.cancelDrawLine)

    def cancelDrawLine(self):
        self.scene.sigMouseClicked.disconnect(self.mouseClicked_line1)

    def drawLineFromValues(self):
        x1, y1, x2, y2, color, accepted = self.dialog.getValues()
        self.shapes.append(QtGui.QGraphicsLineItem(x1,y1,x2,y2))
        self.shapes[-1].setPen(QtGui.QPen(color))
        self.plotView.addItem(self.shapes[-1])

    def updateLine(self, x1, x2, y1, y2):
        self.shapes[-1].setLine(QtCore.QLineF(x1, x2, y1, y2))
        self.dialog.setValuesFromShape()

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
        self.dialog.accepted.disconnect(self.drawLineFromValues)
        self.dialog.accepted.connect(self.applyLineChanges)
        self.dialog.applySig.connect(self.applyLineChanges)
        pos = event.scenePos()
        imgPos = self.viewBox.mapSceneToView(pos)
        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < self.scene.height
                and pos.x() < self.scene.width):

            self.lineStartPos = (imgPos.x(), imgPos.y())

            self.shapes.append(
                    QtGui.QGraphicsLineItem(QtCore.QLineF(
                            imgPos.x(),imgPos.y(),imgPos.x(),imgPos.y())))
            self.plotView.addItem(self.shapes[-1])
            self.shapes[-1].setPen(QtGui.QPen(self.dialog.color))
            self.dialog.setShape(self.shapes[-1])

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

########## Grid Drawing ##############
    # if size is 0, draw grid, else add grid
    def drawGrid(self):
        self.dialog = GridDialog()
        self.scene.sigMouseClicked.connect(self.mouseClicked_grid1)
        self.dialog.accepted.connect(self.drawGridFromValues)
        self.dialog.rejected.connect(self.cancelDrawGrid)

    def cancelDrawGrid(self):
        self.scene.sigMouseClicked.disconnect(self.mouseClicked_grid1)

    def drawGridFromValues(self):
        xPos, yPos, xSize, ySize, rows, cols, color, result = \
            self.dialog.getValues()
        grid = Grid(QtCore.QRectF(
                xPos,yPos,xSize,ySize),rows,cols)
        self.shapes.append(grid)
        self.plotView.addItem(grid)

    def updateGrid(self, x, y, xSize, ySize):
        self.shapes[-1].setRect(QtCore.QRectF(x, y, xSize, ySize))
        self.dialog.setValuesFromShape()

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
        self.dialog.accepted.disconnect(self.drawGridFromValues)
        self.dialog.accepted.connect(self.applyGridChanges)
        self.dialog.applySig.connect(self.applyGridChanges)
        pos = event.scenePos()
        print(pos)
        scene = self.scene
        imgPos = self.viewBox.mapSceneToView(pos)
        print imgPos
        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < scene.height
                and pos.x() < scene.width):

            self.gridStartPos = (imgPos.x(), imgPos.y())
            rows, cols = self.dialog.getRowsCols()
            grid = Grid(QtCore.QRectF(
                imgPos.x(),imgPos.y(),0,0),rows,cols)
            self.shapes.append(grid)
            self.dialog.setShape(grid)
            # self.shapes[-1].setPen(QtGui.QPen(QtCore.Qt.red))
            # self.shapes[-1].setZValue(100)
            #self.shapes[-1].setBrush(QtGui.QBrush(QtCore.Qt.red))
            self.updateGrid(imgPos.x(), imgPos.y(), 0,0)
            grid.color = self.dialog.color
            # gridShapes = self.grid.getShapes()
            # for i in gridShapes:
            #     self.plotView.addItem(i)
            #     i.setPen(QtGui.QPen(QtCore.Qt.red))
            self.plotView.addItem(grid)
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

########## Circle Drawing ###########

    def drawCirc(self):
        self.dialog = CircDialog()
        self.scene.sigMouseClicked.connect(self.mouseClicked_circ1)
        self.dialog.accepted.connect(self.drawCircFromValues)
        self.dialog.rejected.connect(self.cancelDrawCirc)

    def cancelDrawCirc(self):
        self.scene.sigMouseClicked.disconnect(self.mouseClicked_circ1)

    def drawCircFromValues(self):
        x, y, r, color, accepted = self.dialog.getValues()
        self.shapes.append(QtGui.QGraphicsEllipseItem(
                        QtCore.QRectF(x-r,y-r,2*r,2*r)))
        self.shapes[-1].setPen(QtGui.QPen(color))
        self.plotView.addItem(self.shapes[-1])

    def updateCirc(self, x, y, r):
        self.shapes[-1].setRect(QtCore.QRectF(x-r, y-r, 2*r, 2*r))
        self.dialog.setValuesFromShape()

    def mouseMoved_circ(self, pos):
        imgPos = self.viewBox.mapSceneToView(pos)
        scene = self.scene
        # Only update when mouse is in image
        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < scene.height
                and pos.x() < scene.width):

            self.mousePos = (imgPos.x(), imgPos.y())

            r = numpy.sqrt((self.mousePos[0]-self.circCenter[0])**2 +
                        (self.mousePos[1]-self.circCenter[1])**2)

            self.updateCirc(self.circCenter[0], self.circCenter[1], r)

    def mouseClicked_circ1(self, event):
        self.dialog.accepted.disconnect(self.drawCircFromValues)
        self.dialog.accepted.connect(self.applyCircChanges)
        self.dialog.applySig.connect(self.applyCircChanges)
        pos = event.scenePos()
        scene = self.scene
        imgPos = self.viewBox.mapSceneToView(pos)

        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < scene.height
                and pos.x() < scene.width):

            self.circCenter = (imgPos.x(), imgPos.y())
            self.shapes.append(QtGui.QGraphicsEllipseItem(
                    QtCore.QRectF(imgPos.x(), imgPos.y(), 0, 0)))
            self.shapes[-1].setPen(QtGui.QPen(self.dialog.color))
            self.shapes[-1].setZValue(100)

            self.plotView.addItem(self.shapes[-1])
            self.dialog.setShape(self.shapes[-1])

            self.scene.sigMouseMoved.connect(
                    self.mouseMoved_circ)
            self.scene.sigMouseClicked.disconnect(
                    self.mouseClicked_circ1)
            self.scene.sigMouseClicked.connect(
                    self.mouseClicked_circ2)

    def mouseClicked_circ2(self, event):
        pos = event.pos()
        scene = self.scene

        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < scene.height
                and pos.x() < scene.width):

            self.scene.sigMouseMoved.disconnect(
                    self.mouseMoved_circ)
            self.scene.sigMouseClicked.disconnect(
                    self.mouseClicked_circ2)

            self.shapes.updateView()


class ShapeDialog(QtGui.QDialog):

    applySig = QtCore.pyqtSignal()


    def __init__(self, shape=None, parent=None, modal=False):
        super(ShapeDialog, self).__init__(parent)

        # Defualt values for doubleSpinBox max, min
        self.layout = QtGui.QGridLayout(self)
        self.colorButton = QtGui.QPushButton("Color")
        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
            | QtGui.QDialogButtonBox.Apply,
            QtCore.Qt.Horizontal, self)
        # get apply button and connect to apply slot
        self.applyButton = self.buttons.buttons()[2]
        self.applyButton.clicked.connect(self.apply)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.colorButton.clicked.connect(self.getColor)
        self.shape = shape
        if self.shape == None:
            self.applyButton.setEnabled(False)
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
        newColor = QtGui.QColorDialog().getColor(initial=self.color)
        if newColor.isValid():
            self.color = newColor

    def apply(self):
        print "emit"
        self.applySig.emit()

    def setShape(self, shape):
        print "setting shape", shape
        self.shape = shape
        self.applyButton.setEnabled(True)
        self.color = self.shape.pen().color()

    def setDefaultRange(self, spinboxes):
        doubleSpinBoxMin = -100000.0
        doubleSpinBoxMax = 100000.0
        for i in spinboxes:
            i.setRange(doubleSpinBoxMin, doubleSpinBoxMax)

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
        self.yPosBox = QtGui.QDoubleSpinBox()
        self.sizeLabel = QtGui.QLabel("Size (width, height)")
        self.xSizeBox = QtGui.QDoubleSpinBox()
        self.ySizeBox = QtGui.QDoubleSpinBox()

        self.layout.addWidget(self.posLabel)
        self.layout.addWidget(self.xPosBox)
        self.layout.addWidget(self.yPosBox)
        self.layout.addWidget(self.sizeLabel)
        self.layout.addWidget(self.xSizeBox)
        self.layout.addWidget(self.ySizeBox)

        self.layout.addWidget(self.colorButton)
        self.layout.addWidget(self.buttons)
        self.setDefaultRange([self.xPosBox, self.yPosBox, self.xSizeBox,
                              self.ySizeBox])
        self.setLayout(self.layout)

    def setValuesFromShape(self):
        try:
            rect = self.shape.rect().normalized()
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
        self.setDefaultRange([self.x1Box, self.y1Box, self.x2Box, self.y2Box])
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
        self.setDefaultRange([self.xPosBox, self.yPosBox, self.xSizeBox,
                              self.ySizeBox])
        self.rowsBox.setRange(1,100)
        self.columnsBox.setRange(1,100)
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

    def getRowsCols(self):
        return self.rowsBox.value(), self.columnsBox.value()

    def setValuesFromShape(self):
        try:
            rect = self.shape.outRect.rect().normalized()
            self.xPosBox.setValue(rect.x())
            self.yPosBox.setValue(rect.y())
            self.xSizeBox.setValue(rect.width())
            self.ySizeBox.setValue(rect.height())
            self.rowsBox.setValue(self.shape.nRows)
            self.columnsBox.setValue(self.shape.nColumns)
        except AttributeError:
            pass

class CircDialog(ShapeDialog):

    def __init__(self, shape=None, parent=None, modal=False):
        super(CircDialog, self).__init__(shape=shape, parent=parent,
                                        modal = modal)

    def setupUi(self):
        self.posLabel = QtGui.QLabel("Pos (x,y)")
        self.xPosBox = QtGui.QDoubleSpinBox()
        self.yPosBox = QtGui.QDoubleSpinBox()
        self.radiusLabel = QtGui.QLabel("Radius")
        self.radiusBox = QtGui.QDoubleSpinBox()

        self.layout.addWidget(self.posLabel)
        self.layout.addWidget(self.xPosBox)
        self.layout.addWidget(self.yPosBox)
        self.layout.addWidget(self.radiusLabel)
        self.layout.addWidget(self.radiusBox)

        self.layout.addWidget(self.colorButton)
        self.layout.addWidget(self.buttons)
        self.setDefaultRange([self.xPosBox, self.yPosBox, self.radiusBox])
        self.setLayout(self.layout)

    def setValuesFromShape(self):
        try:
            circ = self.shape.rect()
            r = circ.width()/2 # Better way of doing this?
            x, y = circ.x()+r, circ.y()+r
            self.xPosBox.setValue(x)
            self.yPosBox.setValue(y)
            self.radiusBox.setValue(r)
        except AttributeError:
            print "no shape"

    def getValues(self):
        return (self.xPosBox.value(),
                self.yPosBox.value(),
                self.radiusBox.value(),
                self.color,
                self.result())

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
