# Created 2016, Zack Gainsforth

import sys
import os
os.environ['QT_API'] = 'pyqt'
import numpy as np
from MultiLaueGUI import Ui_MultiLaueMainWindow
from PyQt4 import QtGui, QtCore
from skimage.external.tifffile import imsave

import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from ImportScan import ImportScan, ImportScanThread
import BasicProcessing
import MultiLaueProcessing

class MplCanvas(FigureCanvas, QtGui.QWidget):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=3, height=3, dpi=1200):
        self.fig = Figure()#(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        self.DrawInitialFigure()

        #
        FigureCanvas.__init__(self, self.fig)
        self.parent = parent

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        # Enable the ability to note where the user clicks in the figure.
        self.mpl_connect('button_press_event', self.MouseClicked)
        self.mpl_connect('motion_notify_event', self.MouseMoved)

    def DrawInitialFigure(self):
        self.ImageData = np.ones((100,100))
        x = np.linspace(1, 10, 30)
        #self.axes.plot(x, np.sin(x))
        self.axes.imshow(self.ImageData.T, interpolation='none', cmap='gray')
        self.axes.text(35,55, 'No data', color='white')

    def sizeHint(self):
        return QtCore.QSize(300,300)

    def minimalSizeHint(self):
        return QtCore.QSize(100,100)

    def setImageData(self, ImageData):
        # Get the numpy array from the HDF5 object, transpose it for the correct orientation on the screen, get rids of nans,
        # and change any negative infinities to zero (happens in the log images).
        self.ImageData = ImageData[:].T
        self.ImageData[self.ImageData == -np.inf] = 0
        self.axes.imshow(self.ImageData, interpolation='none', cmap='gray')
        #self.fig.tight_layout()
        self.draw()

    def draw(self):
        self.fig.tight_layout()
        super(MplCanvas, self).draw()

    def MouseClicked(self, click):
        # Single clicks occur when dragging and zooming.  So double click is used to select a point.
        if click.dblclick == True:
            # Get the Z value here.
            z = self.ImageData[int(click.ydata+0.5), int(click.xdata+0.5)]
            self.MouseDblClickedCoord = (click.xdata, click.ydata, z)
            self.parent.DoubleClickEvent(self, self.MouseDblClickedCoord)
            return self.MouseDblClickedCoord

    def MouseMoved(self, event):
        if not event.inaxes:
            return
        #print event.xdata, event.ydata

class Main(QtGui.QMainWindow, Ui_MultiLaueMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)
        #self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # Set up the matplotlib plots.
        self.canvasSumImage = MplCanvas(self, width=5, height=4, dpi=100)
        self.toolbarSumImage = NavigationToolbar(self.canvasSumImage, self.widgetMain)
        self.comboSumImage = QtGui.QComboBox()
        self.layoutSumImage.addWidget(self.canvasSumImage)
        self.layoutSumImage.addWidget(self.toolbarSumImage)
        self.layoutSumImage.addWidget(self.comboSumImage)

        # Set up the matplotlib plots.
        #self.widgetMain
        self.canvasSingleImage = MplCanvas(self, width=5, height=4, dpi=100)
        self.toolbarSingleImage = NavigationToolbar(self.canvasSingleImage, self.widgetMain)
        self.comboSingleImage = QtGui.QComboBox()
        self.layoutSingleImage.addWidget(self.canvasSingleImage)
        self.layoutSingleImage.addWidget(self.toolbarSingleImage)
        self.layoutSingleImage.addWidget(self.comboSingleImage)

        # Set up the matplotlib plots.
        self.canvasTopograph = MplCanvas(self, width=5, height=4, dpi=100)
        self.toolbarTopograph = NavigationToolbar(self.canvasTopograph, self.widgetMain)
        self.comboTopograph = QtGui.QComboBox()
        self.layoutTopograph.addWidget(self.canvasTopograph)
        self.layoutTopograph.addWidget(self.toolbarTopograph)
        self.layoutTopograph.addWidget(self.comboTopograph)

        self.canvasSingleImage.updateGeometry()
        self.canvasSumImage.updateGeometry()
        self.canvasTopograph.updateGeometry()
        self.updateGeometry()

        self.statusBar.showMessage('No XRD data loaded.')
        self.statusIndex = 0

        # Connect menu actions
        self.action_Open_Scan.triggered.connect(self.OpenScan)
        self.actionSave_Aggregate_Image.triggered.connect(self.SaveAggregateImage)
        self.actionSave_Topograph_Image.triggered.connect(self.SaveTopographImage)
        self.actionSave_Single_Image.triggered.connect(self.SaveSingleImage)
        self.actionSave_All_Three_Images.triggered.connect(self.SaveThreeImages)
        self.action_Import_Scan.triggered.connect(self.ImportScan)
        self.actionProcess_MultiLaue.triggered.connect(self.ProcessMultiLaue)

        # Connect the combo boxes to their images.
        self.comboSumImage.currentIndexChanged.connect(self.comboSumImage_Changed)
        self.comboTopograph.currentIndexChanged.connect(self.comboTopograph_Changed)
        self.comboSingleImage.currentIndexChanged.connect(self.comboSingleImage_Changed)

    def GetSingleImageCanvas(self):
        return self.canvasSingleImage

    def OpenScan(self):
        FileName = QtGui.QFileDialog.getOpenFileName(self, caption='Open Scan file.',
                                                     filter='HDF5 files (*.hdf5);;All files (*.*)')
        if FileName != '':
            f, Scan = BasicProcessing.LoadScan(str(FileName))
            self.h5 = f
            self.Scan = Scan
            self.statusBar.showMessage('Opened ' + Scan.attrs['ScanName'] + '.')

            # Clear all the images and combo boxes.
            self.canvasSumImage.setImageData(np.zeros((100, 100)))
            self.canvasTopograph.setImageData(np.zeros((100, 100)))
            self.canvasSingleImage.setImageData(np.zeros((100, 100)))
            self.comboSumImage.clear()
            self.comboTopograph.clear()
            self.comboSingleImage.clear()

            # Populate the combobox for the sum image with whatever sum images are in the scan.
            if 'StDevLogImage' in Scan:
                self.comboSumImage.addItem('StDev Image Logarithmic', 'StDevLogImage')
            if 'StDevImage' in Scan:
                self.comboSumImage.addItem('StDev Image', 'StDevImage')
            if 'SumLogImage' in Scan:
                self.comboSumImage.addItem('Sum Image Logarithmic', 'SumLogImage')
            if 'SumImage' in Scan:
                self.comboSumImage.addItem('Sum Image', 'SumImage')

            # Set the index to the first in the list.
            self.comboSumImage.setCurrentIndex(0)
            self.comboSumImage_Changed()

    def SaveAggregateImage(self, FileName=None):
        if FileName is None or FileName == False:
            # Set the default filename to the type of image (SumImage, etc...)
            FileName = str(self.comboSumImage.itemData(self.comboSumImage.currentIndex()).toString()) + '.tif'
            Opts = QtGui.QFileDialog.Option(0x40) #QtGui.QFileDialog.HideNameFilterDetails
            FileName = QtGui.QFileDialog.getSaveFileName(self, caption='Save Aggregate Image.', directory=FileName,
                                                        filter='TIF image (*.tif);;All files(*.*)', options=Opts)
        if FileName != '':
            imsave(FileName, self.canvasSumImage.ImageData[:].astype('float32'))

    def SaveTopographImage(self, FileName=None):
        if FileName is None or FileName == False:
            # Set the default filename to the type of image (SumImage, etc...)
            FileName = 'Topograph.tif'
            Opts = QtGui.QFileDialog.Option(0x40) #QtGui.QFileDialog.HideNameFilterDetails
            FileName = QtGui.QFileDialog.getSaveFileName(self, caption='Save Topograph Image.', directory=FileName,
                                                        filter='TIF image (*.tif);;All files(*.*)', options=Opts)
        if FileName != '':
            imsave(FileName, self.canvasTopograph.ImageData[:].astype('float32'))

    def SaveSingleImage(self, FileName=None):
        if FileName is None or FileName == False:
            # Set the default filename to the type of image (SumImage, etc...)
            FileName = str(self.comboSingleImage.itemData(self.comboSingleImage.currentIndex()).toString()) + '.tif'
            Opts = QtGui.QFileDialog.Option(0x40) #QtGui.QFileDialog.HideNameFilterDetails
            FileName = QtGui.QFileDialog.getSaveFileName(self, caption='Save Aggregate Image.', directory=FileName,
                                                        filter='TIF image (*.tif);;All files(*.*)', options=Opts)
        if FileName != '':
            imsave(FileName, self.canvasSingleImage.ImageData[:].astype('float32'))

    def SaveThreeImages(self):
        FileName = QtGui.QFileDialog.getSaveFileName(self, caption='Save All Three Images.',
                                                     filter='TIF image (*.tif);;All files(*.*)')

        if FileName != '':
            AggregateName = str(self.comboSumImage.itemData(self.comboSumImage.currentIndex()).toString())
            SingleName = str(self.comboSingleImage.itemData(self.comboSingleImage.currentIndex()).toString())

            FileRoot, FileExt = os.path.splitext(str(FileName))
            FileName = FileRoot + AggregateName + FileExt
            self.SaveAggregateImage(FileName)

            FileName = FileRoot + 'Topograph' + FileExt
            self.SaveTopographImage(FileName)

            FileName = FileRoot + SingleName + FileExt
            self.SaveSingleImage(FileName)

    def ImportScan(self):
        FileName = QtGui.QFileDialog.getOpenFileName(self, caption='Open Scan configuration file.', filter='JSON files (*.json);;All files (*.*)')

        if FileName != '':
            PathName, FileName = os.path.split(str(FileName))

            # The import can be many minutes long, so spin this off into a thread.
            self.ImportThread = ImportScanThread(FileName, PathName, "StatusFunc(PyQt_PyObject)")
            #ImportScan(FileName, PathName, self.StatusFunc)

            # Set up a slot for the thread to update status in the GUI.
            self.connect(self.ImportThread, QtCore.SIGNAL("StatusFunc(PyQt_PyObject)"), self.StatusFunc)

            # Now start the thread
            if sys.gettrace() is None:
                print 'Starting thread.'
                self.ImportThread.start()
            else:
                # Don't use a thread when debugging.  Just call the method directly.
                self.ImportThread.run()


    def ProcessMultiLaue(self):
        FileName = QtGui.QFileDialog.getOpenFileName(self, caption='Open Scan file.',
                                                     filter='HDF5 files (*.hdf5);;All files (*.*)')

        if FileName != '':
            # Make a separate thread for this because this can be an hours-long process.
            self.MultiLaueThread = MultiLaueProcessing.ProcessMultiLaueThread(str(FileName), "StatusFunc(PyQt_PyObject)")

            # Set up a slot for the thread to update status in the GUI.
            self.connect(self.MultiLaueThread, QtCore.SIGNAL("StatusFunc(PyQt_PyObject)"), self.StatusFunc)

            # Now start the thread
            if sys.gettrace() is None:
                print 'Starting thread.'
                self.MultiLaueThread.start()
            else:
                # Don't use a thread when debugging.  Just call the method directly.
                self.MultiLaueThread.run()


    def comboSumImage_Changed(self):
        WhichImage = str(self.comboSumImage.itemData(self.comboSumImage.currentIndex()).toString())
        if WhichImage == '':
            return
        self.canvasSumImage.setImageData(self.Scan[WhichImage])

    def comboTopograph_Changed(self):
        pass

    def comboSingleImage_Changed(self):
        WhichImage = str(self.comboSingleImage.itemData(self.comboSingleImage.currentIndex()).toString())
        if WhichImage == '':
            return
        if WhichImage == 'Linear':
            self.canvasSingleImage.setImageData(self.SingleImageRawData)
        if WhichImage == 'Logarithmic':
            self.canvasSingleImage.setImageData(np.log(self.SingleImageRawData))
        if WhichImage == 'Energy':
            self.canvasSingleImage.setImageData(self.EnergyImageRawData)
        if WhichImage == 'EnergyFit':
            self.canvasSingleImage.setImageData(self.EnergyFitImageRawData)

    def StatusFunc(self, StatusStr):
        # The status is ALWAYS written to the status bar.
        self.statusBar.showMessage(StatusStr)
        # When doing loops (like during imports) we get hundreds or thousands of status updates and the GUI doesn't get
        # updated until the loop is done.  So we need to tell the GUI to update every N status messages.
        # If N = 1, then we are updating the status too much and use up all our CPU just writing status messages...
        #if self.statusIndex % 10 == 0:
            #QtGui.QApplication.processEvents()
        #self.statusIndex += 1

    def DoubleClickEvent(self, Canvas, Coord):
        self.statusBar.showMessage('Selected: (x,y)=(%d,%d), value=%g' % Coord)
        # If the sum image was clicked, then that means we need to turn that pixel or region into a topograph.
        if Canvas == self.canvasSumImage:
            self.statusBar.showMessage('Generating topograph from coordinate (x,y)=(%d,%d)...' % Coord[0:2])
            Topo = BasicProcessing.MakeTopographFromCoordinate(self.Scan, Coord)
            self.canvasTopograph.setImageData(Topo)
            self.statusBar.showMessage('Generated topograph from coordinate (x,y)=(%d,%d)' % Coord[0:2])
        if Canvas == self.canvasTopograph:
            # If the user clicked on a topograph pixel, then get the diffraction pattern from that pixel.
            SingleImage, EnergyImage, EnergyFitImage = BasicProcessing.GetSingleImageFromTopographCoordinate(self.Scan, Coord)
            self.SingleImageRawData = SingleImage
            self.EnergyImageRawData = EnergyImage
            self.EnergyFitImageRawData = EnergyFitImage

            # Clear out any old image from the single image and combo box.
            self.canvasSingleImage.setImageData(np.zeros((100, 100)))
            self.comboSingleImage.clear()

            if self.Scan.attrs['ScanType'] == 'MultiLaue':
                # Repopulate the combo box with linear and log options.
                self.comboSingleImage.addItem('Energy', 'Energy')
                self.comboSingleImage.addItem('Energy Fit', 'EnergyFit')
                self.comboSingleImage.addItem('Laue Logarithmic', 'Logarithmic')
                self.comboSingleImage.addItem('Laue Linear', 'Linear')
            else:
                # Repopulate the combo box with linear and log options.
                self.comboSingleImage.addItem('Logarithmic', 'Logarithmic')
                self.comboSingleImage.addItem('Linear', 'Linear')

            # And select the first option.
            self.comboSingleImage.setCurrentIndex(0)
            self.comboSingleImage_Changed()

            self.statusBar.showMessage('Picked single image from topograph from coordinate (x,y)=(%d,%d)' % Coord[0:2])
        if Canvas == self.canvasSingleImage:
            print "Single Image Click not implemented."



if __name__ == '__main__':

    QtApp = QtGui.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(QtApp.exec_())
