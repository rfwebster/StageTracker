# -*- coding: utf-8 -*-
"""
Created on 2021-11-17

@author: Richard F Webster
"""
# Define: Start coord, end coord,

# Process:
# Ask user for start and end co-ordinates
# take image
# start loop while within co-ordinates
#   move stage a bit
#   wait for drift to settle
#   while waiting do auto focus routine (also stigmatism, coma?)
#   focus and stig based on max range or sigma of image - like for tomography - don't save images just read from buffer
#   take image and save
# end loop

# UI - live image, input start and end co-ordinates, how much to move by, magnification, current stage position on chart
# Settings - select image pix and dwell, focus pix and dwell, estimate time remaining

# Anticipated problems
#  - stitching images together, especially when there is no
#  - need to make into a class!!!!!
from utils import *
import numpy as np


from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QWidget
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtTest import QTest
from StageTracker import Ui_MainWindow

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np

try:
    from PyJEM import TEM3
except ImportError:
    from PyJEM.offline import TEM3

    _status = 1  # offline
stage = TEM3.Stage3()
coord = Coord()

print("end of imports")
matplotlib.use("Qt5Agg")


class MplCanvas(FigureCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, parent=None, width=10, height=10, dpi=100, data: Coord = None):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.data = data
        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        self.axes.scatter(self.data.CurrentX, self.data.CurrentY,
                          label="Current", c="blue", marker="x")
        self.axes.scatter(0, 0,
                          label="Centre", c="green", marker="P")
        self.axes.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand",
                         borderaxespad=0., fontsize="small")
        self.axes.axis("equal")

    def update_plot(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        self.axes.cla()
        self.axes.scatter(self.data.CurrentX/1000, self.data.CurrentY/1000,
                          label="Current", c="blue", marker="x")
        self.axes.scatter(0, 0,
                          label="Centre", c="green", marker="P")
        self.axes.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand",
                         borderaxespad=0., fontsize="small")
        self.axes.axis("equal")
        arr = np.array(self.data.snake)
        # print(arr.T)
        try:
            arr = arr.T
            x = arr[0]
            y = arr[1]
            self.axes.plot(x, y, "-k", lw=0.25)
        except IndexError:
            pass

        self.axes.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand",
                         borderaxespad=0., fontsize="small")
        self.axes.axis("equal")
        self.draw()
        
class UpdaterThread(QObject):
    signalExample = pyqtSignal(int, int)
    
    def __init__(self):
        super().__init__()
    
    @pyqtSlot()
    def update(self):
        while True:
            pos = stage.GetPos()
            print("Thread: ", pos[0], pos[1])
            coord.CurrentX, coord.CurrentY = pos[0], pos[1]
            print("Append Snake")
            coord.append_snake()
            print("emit")
            self.signalExample.emit(int(coord.CurrentX), int(coord.CurrentY))
            print("wait)")
            QTest.qWait(500)



class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # image information
        # TODO: get information from actual image - here just made up for debugging script



        # generate microscope classes


        # set up tracker figure
        self.canvas_widget = QWidget(self)
        self.canvas = MplCanvas(self.canvas_widget, width=5, height=4, dpi=100, data=coord)
        self.tracker_holder.addWidget(self.canvas)

        # set up connections

        self.move_Button.clicked.connect(self._move_random)

        self.statusBar().showMessage("Idle")
        self.updater = UpdaterThread()
        self.updaterThread = QThread()
        self.updaterThread.started.connect(self.updater.update)
        self.updater.signalExample.connect(self.signalExample)
        self.updater.moveToThread(self.updaterThread)
        self.updaterThread.start()

        #self._update()

    #############################################################################
    #
    # Run the routine functions
    #
    #############################################################################

    def signalExample(self, pos1, pos2):
        print("in ui class", pos1, pos2)
        self._update()

    def _move_random(self):
        x = np.random.randint(-100000,100000)
        y = np.random.randint(-100000,100000)
        #stage.SetPosition(x,y)
        stage.SetX(x)
        stage.SetY(y)
        self._get_current_position()
        self.statusBar().showMessage("X = {}; Y={}".format(int(x/1000), int(y/1000)))

    ######################################################################################
    #
    # UI Buttons amd functions etc
    #
    ######################################################################################
    def _update(self):
        #self._get_current_position()
        self.canvas.update_plot()
        #QTest.qWait(1000)

    def _get_current_position(self):
        print("getting current position")
        pos = stage.GetPos()
        print(pos[0], pos[1])
        coord.CurrentX, coord.CurrentY = pos[0], pos[1]
        coord.append_snake()
        self.canvas.update_plot()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
