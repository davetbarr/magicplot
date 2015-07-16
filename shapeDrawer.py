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

        # Setup list to hold shapes
        self.shapes = shapeHolder.ShapeContainer()
        self.shapeList.setModel(self.shapes)

        # Connect double click to delete shape
        self.shapeList.doubleClicked.connect(self.shapes.removeShape)

        self.setView(view, item)


    def setView(self, view, item):
        self.plotView = view
        self.plotItem = item
        self.clearShapes()
        # Get the scene object from the view.
        # pyqtgraph imageView is inconsistant, hence try/except
        if view!=None:
            try:
                self.scene = self.plotView.scene()
            except TypeError:
                self.scene = self.plotView.scene

    def clearShapes(self):
        self.shapes.clearShapes()

# Rectangle drawing methods
#############################

    def drawRect(self):

        self.scene.sigMouseClicked.connect(self.mouseClicked_rect1)

        print("DRAW RECT!")
        #self.rects[-1].setBrush(QtGui.QBrush(QtCore.Qt.red))

        # self.painter.fillRect(
        #     self.rects[-1]s[-1], QtGui.QBrush(QtGui.QColor("red")))

        #self.scene.addItem(self.rects[-1])


    def updateRect(self, x, y, xSize, ySize):
        self.shapes[-1].setRect(QtCore.QRectF(x, y, xSize, ySize))

    def mouseMoved_rect(self, pos):
        '''
        method attached to pyqtgraph image widget which gets the mouse position
        If the mouse is in the image, print both the mouse position and
        pixel value to the gui
        '''

        imgPos = self.plotItem.mapFromScene(pos)
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
        pos = event.pos()
        print(pos)
        scene = self.scene
        imgPos = self.plotItem.mapFromScene(pos)
        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < scene.height
                and pos.x() < scene.width):

            self.rectStartPos = (imgPos.x(), imgPos.y())
            self.shapes.append(QtGui.QGraphicsRectItem(
                    QtCore.QRectF(imgPos.x(),imgPos.y(),0,0)))
            self.shapes[-1].setPen(QtGui.QPen(QtCore.Qt.red))
            self.shapes[-1].setZValue(100)
            self.shapes[-1].setBrush(QtGui.QBrush(QtCore.Qt.red))

            self.plotView.addItem(self.shapes[-1])
            #self.rectStartPos = (pos.x(), pos.y())
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

# Line drawing methods
#############################
    def drawLine(self):

        self.scene.sigMouseClicked.connect(self.mouseClicked_line1)

        #self.rect.setBrush(QtGui.QBrush(QtGui.QColor("r")))


    def updateLine(self, x1, x2, y1, y2):
        self.shapes[-1].setLine(QtCore.QLineF(x1, x2, y1, y2))

    def mouseMoved_line(self, pos):
        '''
        method attached to pyqtgraph image widget which gets the mouse position
        If the mouse is in the image, print both the mouse position and
        pixel value to the gui
        '''

        imgPos = self.plotItem.mapFromScene(pos)

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
        pos = event.pos()
        imgPos = self.plotItem.mapFromScene(pos)
        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < self.scene.height
                and pos.x() < self.scene.width):

            self.lineStartPos = (imgPos.x(), imgPos.y())

            self.shapes.append(
                    QtGui.QGraphicsLineItem(QtCore.QLineF(
                            imgPos.x(),imgPos.y(),0,0)))
            imgPos = self.plotItem.mapFromScene(pos)

            self.updateLine(imgPos.x(), imgPos.y(), 0,0)
            self.scene.sigMouseMoved.connect(
                    self.mouseMoved_line)
            self.scene.sigMouseClicked.disconnect(
                    self.mouseClicked_line1)
            self.scene.sigMouseClicked.connect(
                    self.mouseClicked_line2)

    def mouseClicked_line2(self, event):
        print("Line Mouse clicked 2")
        pos = event.pos()
        imgPos = self.plotItem.mapFromScene(pos)
        if      (pos.y() > 0 and pos.x() > 0
                and pos.y() < self.scene.height
                and pos.x() < self.scene.width):
            self.scene.sigMouseMoved.disconnect(
                    self.mouseMoved_line)
            self.scene.sigMouseClicked.disconnect(
                    self.mouseClicked_line2)

            self.shapes.updateView()

class LineDialog(QtGui.QDialog):
    def __init__(self):
        pass
