"""
Simpe live updating example using magicplot
"""

import magicplot
import time
import numpy

from PyQt5 import QtCore

class DummyCCD():

    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y
        self.data = numpy.random.normal(0,1,size=(10, self.size_x, self.size_y))
        self.i = 0

    def grab_frame(self):
        self.i += 1
        return self.data[self.i%10]

class UpdateThread(QtCore.QThread):
    """
    QThread to update plot. Taken from AOplot.
    """
    # Create signals:
    # (a) for updating the plot when new data arrives:
    updateSignal       = QtCore.pyqtSignal(object)

    def __init__(self, decimation):
        super(UpdateThread, self).__init__()
        self.decimation = decimation
        self.ccd = DummyCCD(100,100)

    # This function is called when you say "updateThread.start()":
    def run(self):
        while self.isRunning:
            frame = self.ccd.grab_frame()
            self.emitUpdateSignal(frame)
            time.sleep(1./self.decimation)

    # This function is called by the RTC everytime new data is ready:
    def emitUpdateSignal(self, data ):
        """
        Emit the signal saying that new data is ready, and pass the data to the
        slot that is connected to this signal.

        Args:
            data : ["data", streamname, (data, frame time, frame number)]
                   this is the structure of a data package coming from darc

        Returns:
            nothing
        """
        self.updateSignal.emit( data)


app = magicplot.pyqtgraph.mkQApp()
plt = magicplot.MagicPlot()
im = plt.getImageItem()
plt.show()
t = UpdateThread(10)
t.updateSignal.connect(im.setData)
t.start()
app.exec_()
t.exit()


