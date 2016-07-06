# Created 2016, Zack Gainsforth

import sys
import os
os.environ['QT_API'] = 'pyqt'

import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import numpy as np


from PyQt4 import QtGui, QtCore
from MultiLaueGUI import Ui_MultiLaueMainWindow

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas, QtGui.QWidget):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=3, height=3, dpi=1200):
        fig = Figure()#(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        #self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        self.ImageData = np.ones((100,100))
        x = np.linspace(1, 10, 30)
        #self.axes.plot(x, np.sin(x))
        self.axes.imshow(self.ImageData, interpolation='none', cmap='gray')
        self.axes.text(35,55, 'No data', color='white')

    def sizeHint(self):
        return QtCore.QSize(300,300)

    def minimalSizeHint(self):
        return QtCore.QSize(100,100)

class Main(QtGui.QMainWindow, Ui_MultiLaueMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # Set up the matplotlib plots.
        self.canvasSumImage = MplCanvas(self.widgetMain, width=5, height=4, dpi=100)
        self.layoutSumImage.addWidget(self.canvasSumImage)

        # Set up the matplotlib plots.
        self.canvasSingleImage = MplCanvas(self.widgetMain, width=5, height=4, dpi=100)
        self.layoutSingleImage.addWidget(self.canvasSingleImage)

        # Set up the matplotlib plots.
        self.canvasTopograph = MplCanvas(self.widgetMain, width=5, height=4, dpi=100)
        self.layoutTopograph.addWidget(self.canvasTopograph)

        self.canvasSingleImage.updateGeometry()
        self.canvasSumImage.updateGeometry()
        self.canvasTopograph.updateGeometry()
        self.updateGeometry()

if __name__ == '__main__':

    QtApp = QtGui.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(QtApp.exec_())
