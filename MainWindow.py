# Created 2016, Zack Gainsforth
import matplotlib
#matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import numpy as np

from PyQt4 import QtGui
from MultiLaueGUI import Ui_MultiLaueGUI

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# class InlineCanvas(FigureCanvas):
#     def __init__(self, parent=None, width=5, height=4, dpi=100):
#         fig = Figure(figsize=(width, height), dpi=dpi)
#         self.axes = fig.add_subplot(111)
#
#         t = np.arange(0.0, 3.0, 0.01)
#         s = np.sin(2*np.pi*t)
#         self.axes.plot(t,s)
#

class Main(QtGui.QMainWindow, Ui_MultiLaueGUI):
    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)

    def addmpl(self, fig):
        self.canvas = FigureCanvas(fig)
        self.splitter.addWidget(self.canvas)
        self.canvas.draw()

if __name__ == '__main__':
    import sys

    fig1 = Figure()
    ax = fig1.add_subplot(111)
    ax.plot(np.random.rand(20))


    QtApp = QtGui.QApplication(sys.argv)
    main = Main()
    main.addmpl(fig1)
    main.show()

    # MainWindow = QtGui.QMainWindow()
    # GUI = Ui_MultiLaueGUI()
    # GUI.setupUi(MainWindow)
    #
    # it = InlineCanvas(GUI)
    # GUI.splitter.addWidget(it)
    #
    # MainWindow.show()

    sys.exit(QtApp.exec_())
