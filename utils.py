import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtTest import QTest

import matplotlib

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from scipy import signal

try:
    from PyJEM import detector
    from PyJEM import TEM3
except(ImportError):
    from PyJEM.offline import detector
    from PyJEM.offline import TEM3

    _status = 1  # offline
matplotlib.use('Qt5Agg')


def correlate(img1: np.array, img2: np.array):
    corr = signal.correlate2d(img1, img2)
    y, x = np.unravel_index(np.argmax(corr), corr.shape)  # find the match
    return [x, y]


class Coord:
    """
    class for holding the start end and current positions of the stage
    """
    def __init__(self):
        self.CurrentX: float = 0
        self.CurrentY: float = 0

        self.StartX: float = 0
        self.StartY: float = 0

        self.EndX: float = 0
        self.EndY: float = 0

        self.snake = list()
        self.snake_length = 999

    def get_min(self):
        """
        get the minima co-ordinates
        :return:
        the minimum X and the minimum Y co-ordinate
        """
        return [min([self.StartX, self.EndX]), min([self.StartY, self.EndY])]

    def get_max(self):
        """
        get the maxima co-ordinates
        :return:
        the minimum X and the minimum Y co-oordinate
        """
        return [max([self.StartX, self.EndX]), max([self.StartY, self.EndY])]

    def get_range(self):
        """
        get the ange of co-ordinates
        :return:
        the minimium and maximum X and Y co-ordinates as a list
        """
        return [self.get_min(),
                self.get_max()]

    def append_snake(self):
        self.snake.append([self.CurrentX/1000, self.CurrentY/1000])
        if len(self.snake) >= self.snake_length:
            self.snake = self.snake[-self.snake_length:]
