# Created 2016, Zack Gainsforth

import sys
import os
os.environ['QT_API'] = 'pyqt'
import numpy as np
from MultiLaueGUI import Ui_MultiLaueMainWindow
from AboutBox import Ui_AboutDialog
from PyQt4 import QtGui, QtCore
from skimage.external.tifffile import imsave
import json

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
        #self.axes.text(35,55, 'No data', color='white')

    def sizeHint(self):
        return QtCore.QSize(300,300)

    def minimalSizeHint(self):
        return QtCore.QSize(100,100)

    def setImageData(self, ImageData):
        # Get the numpy array from the HDF5 object, transpose it for the correct orientation on the screen, get rids of nans,
        # and change any negative infinities to zero (happens in the log images).
        self.ImageData = ImageData[:].T
        self.ImageData[np.isinf(self.ImageData)] = 0
        self.ImageData = np.nan_to_num(self.ImageData)
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

class AboutBoxDialog(QtGui.QDialog, Ui_AboutDialog):
    def __init__(self):
        super(AboutBoxDialog, self).__init__()
        self.setupUi(self)

class Main(QtGui.QMainWindow, Ui_MultiLaueMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)
        #self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.setWindowIcon(QtGui.QIcon(":/Icons/Laue"))
        QtApp.setWindowIcon(QtGui.QIcon(":/Icons/Laue"))

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
        self.actionClose.triggered.connect(self.CloseScan)
        self.actionOpen_GitHub_Website.triggered.connect(self.OpenGitHub)
        self.actionAbout_MultiLaue.triggered.connect(self.CallAboutBox)

        # Connect the combo boxes to their images.
        self.comboSumImage.currentIndexChanged.connect(self.comboSumImage_Changed)
        self.comboTopograph.currentIndexChanged.connect(self.comboTopograph_Changed)
        self.comboSingleImage.currentIndexChanged.connect(self.comboSingleImage_Changed)

        # Set up members placeholders for threads that are used later.
        self.ImportThread = None
        self.MultiLaueThread = None

        #  Read in the defaults file if it exists ,or populate it with defaults.
        if os.path.exists('MultiLaueDefaults.json'):
            with open('MultiLaueDefaults.json', 'r') as f:
                DefaultsStr = f.read()

            self.Defaults = json.loads(DefaultsStr)
        else:
            self.Defaults = dict()
            self.Defaults['DefaultFileDialogDir'] = os.getcwd()

            DefaultsStr = json.dumps(self.Defaults, indent=4)

            with open('MultiLaueDefaults.json', 'w') as f:
                f.write(DefaultsStr)

    def CallAboutBox(self):
        Dlg = AboutBoxDialog()
        Dlg.exec_()

    def closeEvent(self, event):
        # Before closing, make sure we write out the defaults to disk.
        DefaultsStr = json.dumps(self.Defaults, indent=4)

        with open('MultiLaueDefaults.json', 'w') as f:
            f.write(DefaultsStr)

        event.accept()

    def OpenGitHub(self):
        import webbrowser

        webbrowser.open('https://github.com/ZGainsforth/MultiLaue')

    def CloseScan(self, quiet=False):
        try:
            self.h5.close()
        except:
            pass
        self.Scan = None
        self.h5 = None
        # Clear all the images and combo boxes.
        self.canvasSumImage.setImageData(np.zeros((100, 100)))
        self.canvasTopograph.setImageData(np.zeros((100, 100)))
        self.canvasSingleImage.setImageData(np.zeros((100, 100)))
        self.comboSumImage.clear()
        self.comboTopograph.clear()
        self.comboSingleImage.clear()
        if quiet == False:
            self.statusBar.showMessage('Closed Scan.')

    def GetSingleImageCanvas(self):
        return self.canvasSingleImage

    def OpenScan(self):

        # Get the name of the file to open from the user.  Move to the default path (i.e. the last one used by the user) so the dialogs are all staying within the same directory.
        FileName = os.path.join(self.Defaults['DefaultFileDialogDir'], '*.hdf5')
        FileName = QtGui.QFileDialog.getOpenFileName(self, caption='Open Scan file.', directory=FileName,
                                                     filter='HDF5 files (*.hdf5);;All files (*.*)')
        if FileName != '':
            self.CloseScan(quiet=True)

            # Store the default path now that the user has selected a file.
            self.Defaults['DefaultFileDialogDir'], _ = os.path.split(str(FileName))

            f, Scan = BasicProcessing.LoadScan(str(FileName))
            self.h5 = f
            self.Scan = Scan
            self.statusBar.showMessage('Opened ' + Scan.attrs['ScanName'] + '.')

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
            FileName = os.path.join(self.Defaults['DefaultFileDialogDir'], str((self.comboSumImage.itemData(self.comboSumImage.currentIndex()).toString()) + '.tif'))
            Opts = QtGui.QFileDialog.Option(0x40) #QtGui.QFileDialog.HideNameFilterDetails
            FileName = QtGui.QFileDialog.getSaveFileName(self, caption='Save Aggregate Image.', directory=FileName,
                                                        filter='TIF image (*.tif);;All files(*.*)', options=Opts)
        if FileName != '':
            # Store the default path now that the user has selected a file.
            self.Defaults['DefaultFileDialogDir'], _ = os.path.split(str(FileName))
            # Write the image file to disk.
            imsave(FileName, self.canvasSumImage.ImageData[:].astype('float32'))

    def SaveTopographImage(self, FileName=None):
        if FileName is None or FileName == False:
            # Set the default filename to the type of image (SumImage, etc...)
            FileName = os.path.join(self.Defaults['DefaultFileDialogDir'], str(self.comboTopograph.itemData(self.comboTopograph.currentIndex()).toString()) + '.tif')
            Opts = QtGui.QFileDialog.Option(0x40) #QtGui.QFileDialog.HideNameFilterDetails
            FileName = QtGui.QFileDialog.getSaveFileName(self, caption='Save Topograph Image.', directory=FileName,
                                                        filter='TIF image (*.tif);;All files(*.*)', options=Opts)
        if FileName != '':
            # Store the default path now that the user has selected a file.
            self.Defaults['DefaultFileDialogDir'], _ = os.path.split(str(FileName))
            # Write the image file to disk.
            imsave(FileName, self.canvasTopograph.ImageData[:].astype('float32'))

    def SaveSingleImage(self, FileName=None):
        if FileName is None or FileName == False:
            # Set the default filename to the type of image (SumImage, etc...)
            FileName = os.path.join(self.Defaults['DefaultFileDialogDir'], str(self.comboSingleImage.itemData(self.comboSingleImage.currentIndex()).toString()) + '.tif')
            Opts = QtGui.QFileDialog.Option(0x40) #QtGui.QFileDialog.HideNameFilterDetails
            FileName = QtGui.QFileDialog.getSaveFileName(self, caption='Save Aggregate Image.', directory=FileName,
                                                        filter='TIF image (*.tif);;All files(*.*)', options=Opts)
        if FileName != '':
            # Store the default path now that the user has selected a file.
            self.Defaults['DefaultFileDialogDir'], _ = os.path.split(str(FileName))
            # Write the image file to disk.
            imsave(FileName, self.canvasSingleImage.ImageData[:].astype('float32'))

    def SaveThreeImages(self):
        try:
            # The best option is to default naming the images by the scan name.
            FileName = os.path.join(self.Defaults['DefaultFileDialogDir'], self.Scan.attrs['ScanName']+'_.tif')
        except:
            # But if no scan is open right now, then save the user some embarassement.
            QtGui.QMessageBox.warning(self, 'MultiLaue', 'No scan is open now.  No data to save.',
                                      QtGui.QMessageBox.NoButton, QtGui.QMessageBox.Warning)
            return

        FileName = QtGui.QFileDialog.getSaveFileName(self, caption='Save All Three Images.', directory=FileName,
                                                     filter='TIF image (*.tif);;All files(*.*)')

        if FileName != '':
            # Store the default path now that the user has selected a file.
            self.Defaults['DefaultFileDialogDir'], _ = os.path.split(str(FileName))

            AggregateName = str(self.comboSumImage.itemData(self.comboSumImage.currentIndex()).toString())
            TopographName = str(self.comboTopograph.itemData(self.comboTopograph.currentIndex()).toString())
            SingleName = str(self.comboSingleImage.itemData(self.comboSingleImage.currentIndex()).toString())

            FileRoot, FileExt = os.path.splitext(str(FileName))
            FileName = FileRoot + AggregateName + FileExt
            self.SaveAggregateImage(FileName)

            FileName = FileRoot + TopographName + FileExt
            self.SaveTopographImage(FileName)

            FileName = FileRoot + SingleName + FileExt
            self.SaveSingleImage(FileName)

    def ImportScan(self):
        # Only allow one import at a time.
        if self.ImportThread is not None:
            QtGui.QMessageBox.warning(self, 'MultiLaue',
                                      'Can only import one scan at a time.  Please wait for the previous import to finish.',
                                      QtGui.QMessageBox.NoButton, QtGui.QMessageBox.Warning)
            return

        FileName = os.path.join(self.Defaults['DefaultFileDialogDir'], '*.json')
        FileName = QtGui.QFileDialog.getOpenFileName(self, caption='Open Scan configuration file.', directory=FileName, filter='JSON files (*.json);;All files (*.*)')

        if FileName != '':
            PathName, FileName = os.path.split(str(FileName))
            self.Defaults['DefaultFileDialogDir'] = PathName

            # The import can be many minutes long, so spin this off into a thread.
            self.ImportThread = ImportScanThread(FileName, PathName, "StatusFunc(PyQt_PyObject)")
            #ImportScan(FileName, PathName, self.StatusFunc)

            # Set up a slot for the thread to update status in the GUI.
            self.connect(self.ImportThread, QtCore.SIGNAL("StatusFunc(PyQt_PyObject)"), self.StatusFunc)
            self.connect(self.ImportThread, QtCore.SIGNAL('finished()'), self.ImportScanFinished)

            # Now start the thread
            if sys.gettrace() is None:
                self.ImportThread.start()
            else:
                # Don't use a thread when debugging.  Just call the method directly.
                self.ImportThread.run()

    def ImportScanFinished(self):
        self.ImportThread = None


    def ProcessMultiLaue(self):
        # Only allow one import at a time.
        if self.MultiLaueThread is not None:
            QtGui.QMessageBox.warning(self, 'MultiLaue',
                                      'Can only process one MultiLaue data set at a time.  Please wait for the previous processing to complete.',
                                      QtGui.QMessageBox.NoButton, QtGui.QMessageBox.Warning)
            return

        FileName = os.path.join(self.Defaults['DefaultFileDialogDir'], '*.hdf5')
        FileName = QtGui.QFileDialog.getOpenFileName(self, caption='Open Scan file.', directory=FileName,
                                                     filter='HDF5 files (*.hdf5);;All files (*.*)')

        if FileName != '':
            # Store the default path now that the user has selected a file.
            self.Defaults['DefaultFileDialogDir'], _ = os.path.split(str(FileName))

            # Make a separate thread for this because this can be an hours-long process.
            self.MultiLaueThread = MultiLaueProcessing.ProcessMultiLaueThread(str(FileName), "StatusFunc(PyQt_PyObject)")

            # Set up a slot for the thread to update status in the GUI.
            self.connect(self.MultiLaueThread, QtCore.SIGNAL("StatusFunc(PyQt_PyObject)"), self.StatusFunc)
            self.connect(self.MultiLaueThread, QtCore.SIGNAL('finished()'), self.ProcessMultiLaueFinished)

            # Now start the thread
            if sys.gettrace() is None:
                self.MultiLaueThread.start()
            else:
                # Don't use a thread when debugging.  Just call the method directly.
                self.MultiLaueThread.run()

    def ProcessMultiLaueFinished(self):
        print 'ProcessMultiLaueFinished called'
        self.MultiLaueThread = None

    def comboSumImage_Changed(self):
        WhichImage = str(self.comboSumImage.itemData(self.comboSumImage.currentIndex()).toString())
        if WhichImage == '':
            return
        self.canvasSumImage.setImageData(self.Scan[WhichImage])

    def comboTopograph_Changed(self):
        WhichImage = str(self.comboTopograph.itemData(self.comboTopograph.currentIndex()).toString())
        if WhichImage == '':
            return
        if WhichImage == 'Topograph':
            self.canvasTopograph.setImageData(self.TopographRawData)
        if WhichImage == 'TopographLog':
            self.canvasTopograph.setImageData(np.log(self.TopographRawData))


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


    def DoubleClickEvent(self, Canvas, Coord):
        self.statusBar.showMessage('Selected: (x,y)=(%d,%d), value=%g' % Coord)
        # If the sum image was clicked, then that means we need to turn that pixel or region into a topograph.
        if Canvas == self.canvasSumImage:
            # Make the topograph.
            self.statusBar.showMessage('Generating topograph from coordinate (x,y)=(%d,%d)...' % Coord[0:2])
            Topo = BasicProcessing.MakeTopographFromCoordinate(self.Scan, Coord)

            # Store the raw data for the topograph.  This will be plotted when we select a combo box item.
            self.TopographRawData = Topo

            # Repopulate the combo box.
            self.comboTopograph.clear()
            self.comboTopograph.addItem('Topograph Logarithmic', 'TopographLog')
            self.comboTopograph.addItem('Topograph Linear', 'Topograph')

            # And select the first option.
            self.comboTopograph.setCurrentIndex(0)
            self.comboTopograph_Changed()

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
    QtApp.setApplicationName('MultiLaue')

    from sys import platform

    # # Check if we're on OS X, first.
    # if platform == 'darwin':
    #     from Foundation import NSBundle
    #
    #     bundle = NSBundle.mainBundle()
    #     if bundle:
    #         info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
    #         if info and info['CFBundleName'] == 'Python':
    #             info['CFBundleName'] = 'MultiLaue'

    main = Main()
    main.show()
    sys.exit(QtApp.exec_())
