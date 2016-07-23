# Created 2016, Zack Gainsforth

import os
import sys

os.environ['QT_API'] = 'pyqt'
import numpy as np
from MultiLaueGUI import Ui_MultiLaueMainWindow
from AboutBox import Ui_AboutDialog
from PyQt4 import QtGui, QtCore
from skimage.external.tifffile import imsave
import json
import matplotlib
from DetectorGeometry import DetectorGeometry

matplotlib.use('Qt4Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from ImportScan import ImportScanThread
import BasicProcessing
import MultiLaueProcessing
from DataReadout import Ui_DataReadout
from collections import OrderedDict


class DataReadoutControl(QtGui.QWidget, Ui_DataReadout):
    def __init__(self, parent=None):
        super(DataReadoutControl, self).__init__()
        self.setupUi(self)
        self.parent = parent

        # Give the text boxes a fixed width that fits the number strings we will send.
        TestStr = '{:>10.3g}'.format(0.0)
        fnt = QtGui.QFont("Courier", 13)
        fm = QtGui.QFontMetrics(fnt)
        pixWide = fm.width(TestStr)
        self.txtMin.setFixedWidth(pixWide)
        self.txtMax.setFixedWidth(pixWide)

        # Figure out the height of the greek symbols (not the same as english) and format all the labels to be the larger height.
        TestStr = u'\u03c7 = '
        pixWide = fm.width(TestStr)
        pixHeight = fm.height()
        self.lbl_x.setFixedHeight(pixHeight)
        self.lbl_y.setFixedHeight(pixHeight)
        self.lbl_I.setFixedHeight(pixHeight)
        self.lbl_Counts.setFixedHeight(pixHeight)
        self.lbl_d.setFixedHeight(pixHeight)
        self.lbl_chi.setFixedHeight(pixHeight)
        self.lbl_twotheta.setFixedHeight(pixHeight)
        self.lbl_FitVal.setFixedHeight(pixHeight)
        self.lbl_mean.setFixedHeight(pixHeight)
        self.lbl_sigma.setFixedHeight(pixHeight)

        # And have the control size itself up.
        # self.setxy(0, 0)
        self.lastx = 0
        self.lasty = 0

        self.txtMin.editingFinished.connect(self.txtMinMaxEdited)
        self.txtMax.editingFinished.connect(self.txtMinMaxEdited)
        self.txtMin.textChanged.connect(self.txtMinMaxEditing)
        self.txtMax.textChanged.connect(self.txtMinMaxEditing)
        self.btn_AutoScale.clicked.connect(self.AutoScaleButton)

        # Plancks constant.
        self.h = 6.626070040e-34  # J*S
        # Speed of light
        self.c = 299792458  # m/s
        self.q = 1.602177e-19
        self.hcover2q = self.h*self.c/2/self.q


    def txtMinMaxEditing(self):
        self.MinText = self.txtMin.text()
        self.MaxText = self.txtMax.text()

    def txtMinMaxEdited(self):
        # We want to update the image when the values the user typed are valid.
        DataOK = True

        try:
            MinVal = float(self.MinText)
        except:
            # If they can't be formatted as numbers, then change the text red.
            self.txtMin.setStyleSheet('color: rgb(255,0,0);')
            DataOK = False
        else:
            if len(self.txtMin.styleSheet()) != 0:
                self.txtMin.setStyleSheet('')

        try:
            MaxVal = float(self.MaxText)
        except:
            self.txtMax.setStyleSheet('color: rgb(255,0,0);')
            DataOK = False
        else:
            if len(self.txtMax.styleSheet()) != 0:
                self.txtMax.setStyleSheet('')

        # Move out if the data is not OK.
        if not DataOK:
            return

        # Plot the image with the new vlim settings.
        Image = self.parent.Images[self.parent.CanvasViewSettings['CurrentImageKey']]
        Image['vlim'] = np.array([MinVal, MaxVal])
        self.parent.plotImage()

    def get_d_twotheta_chi(self, x, y, E):
        try:
            g = self.DetectorGeometry
        except:
            self.DetectorGeometry = DetectorGeometry(Calibration=self.parent.parent.Scan['Calibration'].attrs)
            g = self.DetectorGeometry

        twotheta, chi, kmag = g.GetTwoThetaChi(x, y)

        if E is None or E == 0:
            d = None
        else:
            d = self.hcover2q/E/np.sin(np.radians(twotheta/2))*1e10 # Braggs law for d in A, using energy in eV.

        return d, twotheta, chi

    def setxy(self, x, y):
        # There are several types of image which cause the DataReadoutControl to populate the read out differently.  These are the possible
        # image types:
        # 'StDevLogImage', 'StDevImage', 'SumLogImage', 'SumImage', 'Topograph', 'TopographLog', 'Linear', 'Logarithmic', 'Energy', 'EnergyFit'

        # Store the x and y for future use (calling setxy to refresh controls).
        self.lastx = x
        self.lasty = y

        # x and y are always valid and can be reported for every image.
        self.lbl_x.setText('x = %13d' % int(x + 0.5))
        self.lbl_y.setText('y = %13d' % int(y + 0.5))

        ImageKey = self.parent.CanvasViewSettings['CurrentImageKey']

        # If no image is loaded, then make everything blank except x and y.
        if ImageKey == 'NoData':
            # If there is no image data, then we clear out all the other fields.
            self.lbl_I.setText('')
            # self.lbl_Counts.setText('')
            self.lbl_Counts.setText('{:>17s}'.format(' '))
            self.lbl_d.setText('')
            self.lbl_chi.setText('')
            self.lbl_twotheta.setText('')
            # self.lbl_FitVal.setText('')
            self.lbl_FitVal.setText('{:>14s}'.format(' '))
            self.lbl_mean.setText('')
            self.lbl_sigma.setText('')
            self.txtMin.setText('')
            self.txtMax.setText('')
            return

        # Note the current image.
        Image = self.parent.Images[ImageKey]

        # The I/E field contains either the intensity or energy.  Get the data value from the image.
        # If energy, we will revisit this field below.
        if 'Energy' not in ImageKey:
            z = Image['ImageData'][int(y + 0.5), int(x + 0.5)]
            self.lbl_I.setText('I = %13g' % z)

            if 'Log' in ImageKey:
                self.lbl_Counts.setText('Counts = %8.3g' % np.exp(z))
            else:
                self.lbl_Counts.setText('Counts = %8.3g' % z)

        # d, chi, and twotheta are ignored in topographs and calculated otherwise.
        if 'Topograph' in ImageKey:
            self.lbl_chi.setText('')
            self.lbl_twotheta.setText('')
            self.lbl_FitVal.setText('{:>14s}'.format(' '))
        elif 'Energy' in ImageKey:
            # For the energy images, we need to report counts from the raw laue, the fit and the energy.  All this data is stored in the
            # main class (parent of the canvas) if the Energy or energy fit images are loaded.
            # Counts = self.parent.parent.SingleImageRawData[int(y + 0.5), int(x + 0.5)]
            # Energy = self.parent.parent.EnergyImageRawData[int(y + 0.5), int(x + 0.5)]
            # Fit = self.parent.parent.EnergyFitImageRawData[int(y + 0.5), int(x + 0.5)]
            Counts = self.parent.Images['Linear']['ImageData'][int(y + 0.5), int(x + 0.5)]
            Energy = self.parent.Images['Energy']['ImageData'][int(y + 0.5), int(x + 0.5)]
            Fit = self.parent.Images['EnergyFit']['ImageData'][int(y + 0.5), int(x + 0.5)]

            self.lbl_I.setText('E = %9.3g keV' % Energy)
            self.lbl_Counts.setText('Counts = %8.3g' % Counts)
            self.lbl_FitVal.setText('Fit = {:>8.3g}'.format(Fit))  # 'Fit = %8.6g' % Fit)

            (d, twotheta, chi) = self.get_d_twotheta_chi(x, y, Energy)
            if d is not None:
                self.lbl_d.setText(u'd = %9.3g \u212B' % d)
            else:
                self.lbl_d.setText(u'd =        n/a')
            self.lbl_twotheta.setText(u'2\u03b8 = %5.3g deg' % twotheta)
            #self.lbl_chi.setText(u'\u03c7 = %4.3g deg' % chi)
            self.lbl_chi.setText('')

        else:
            self.lbl_FitVal.setText('{:>14s}'.format(' '))
            (d, twotheta, chi) = self.get_d_twotheta_chi(x, y, None)
            self.lbl_d.setText('') # We can only get d for energy images.
            self.lbl_twotheta.setText(u'2\u03b8 = %5.3g deg' % twotheta)
            #self.lbl_chi.setText(u'\u03c7 = %4.3g deg' % chi)
            self.lbl_chi.setText('')

        self.lbl_mean.setText(u'Mean = %8.3g' % (Image['mean']))
        self.lbl_sigma.setText(u'\u03c3 = %11.3g' % (Image['std']))

        if np.abs(Image['vlim'][0]) < 10000:
            self.txtMin.setText('{:>10.2f}'.format(Image['vlim'][0]))
        else:
            self.txtMin.setText('{:>10.2e}'.format(Image['vlim'][0]))
        if np.abs(Image['vlim'][1]) < 10000:
            self.txtMax.setText('{:>10.2f}'.format(Image['vlim'][1]))
        else:
            self.txtMax.setText('{:>10.2e}'.format(Image['vlim'][1]))

    def AutoScaleButton(self):
        self.parent.DoAutoScale()

class MplCanvas(FigureCanvas, QtGui.QWidget):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=3, height=3, dpi=1200):
        # Make a figure and axes.
        self.fig = Figure()  # (figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)
        # No numbers along the axes.
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)
        self.fig.tight_layout()

        FigureCanvas.__init__(self, self.fig)
        self.parent = parent

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def AfterInitialize(self, ComboBox, Toolbar, DataReadout):
        # We want handles to the nav toolbar and to the readout control, but they want handles to us.  So __init__ has the minimum necessary
        # and this actually does the rest of the initialization.
        self.ComboBox = ComboBox
        self.Toolbar = Toolbar
        self.DataReadout = DataReadout

        # Enable the ability to note where the user clicks in the figure.
        self.mpl_connect('button_press_event', self.MouseClicked)
        self.mpl_connect('motion_notify_event', self.MouseMoved)
        self.mpl_connect('draw_event', self.WasDrawn)

        self.InitCanvasData()

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    def minimalSizeHint(self):
        return QtCore.QSize(100, 100)

    def plotImage(self):
        Image = self.Images[self.CanvasViewSettings['CurrentImageKey']]
        # And plot it.
        self.axes.imshow(Image['ImageData'], interpolation='none', cmap='gray', vmin=Image['vlim'][0], vmax=Image['vlim'][1])
        self.axes.set_xlim(self.CanvasViewSettings['xlim'])
        self.axes.set_ylim(self.CanvasViewSettings['ylim'])
        self.draw()

        # Tell the data readout to refresh.
        try:
            self.DataReadout.setxy(self.DataReadout.lastx, self.DataReadout.lasty)
        except:
            pass

    def draw(self):
        self.fig.tight_layout()
        super(MplCanvas, self).draw()

    def InitCanvasData(self, InputImages=None):
        if InputImages == None:
            # To reset, we are going to make a blank image dataset and populate our memory structures with it.
            ImageData = np.zeros((100, 100))

            self.Images = OrderedDict()
            self.Images['NoData'] = OrderedDict()
            self.Images['NoData']['ImageData'] = ImageData
            self.Images['NoData']['ImageName'] = 'No Data'
        else:
            self.Images = InputImages

        # Settings for the canvas that apply to any image it shows.
        self.CanvasViewSettings = dict()
        self.CanvasViewSettings['CurrentImageKey'] = list(self.Images.keys())[0]

        # Don't allow the changed signal to trigger until we're done populating.
        self.ComboBox.blockSignals(True)
        self.ComboBox.clear()

        # Now, populate data structures.
        for ImageKey, Image in self.Images.items():
            if 'Shape' not in self.CanvasViewSettings:
                # Make settings for viewing the image that apply to all images on this canvas based on the first image.
                shape = Image['ImageData'].shape
                self.CanvasViewSettings['xlim'] = (None, None)  # These can change as the user zooms in and out.
                self.CanvasViewSettings['ylim'] = (None, None)
                self.CanvasViewSettings['Shape'] = shape  # This is to ensure all the images are the same size.
            else:
                # For all subsequent images, just make sure they have the same dimension.
                assert Image['ImageData'].shape == self.CanvasViewSettings['Shape']

            # Add this Image to the Combo box.
            self.ComboBox.addItem(Image['ImageName'], ImageKey)
            # Get basic stats about the image such as the mean value, and such.
            self.AnalyzeImage(self.Images[ImageKey])

        # Enable the combo box again.
        self.ComboBox.setCurrentIndex(0)
        self.ComboBox.blockSignals(False)

        # Plot it.
        self.plotImage()

        # Update the DataReadout
        # self.DataReadout.setxy(0,0)

    def SetCurrentImage(self, ImageKey):
        assert ImageKey in self.Images.keys(), 'Cannot set to image %s -- not in the list for this canvas.' % ImageKey
        self.CanvasViewSettings['CurrentImageKey'] = ImageKey
        self.plotImage()
        # self.ResetFigureZoom() # Note this includes a redraw.

    def AnalyzeImage(self, Image):

        Image['max'] = np.max(Image['ImageData'])
        Image['min'] = np.min(Image['ImageData'])
        Image['mean'] = np.mean(Image['ImageData'])
        Image['std'] = np.std(Image['ImageData'])
        Image['vlim'] = self.GetAutoScale(Image) #np.array([Image['mean'] - 2 * Image['std'], Image['mean'] + 2 * Image['std']])
        return

    def GetAutoScale(self, Image):
        # Energy images are different.  Most of the pixels are 0.  So we're going to treat them as nan and then compute.
        if 'Energy' in Image['ImageName']:
            TempImage = np.copy(Image['ImageData'])
            TempImage[TempImage == 0] = np.nan
            mean = np.nanmean(TempImage)
            std = np.nanstd(TempImage)
        else:
            mean = Image['mean']
            std = Image['std']

        # Autoscale is skew for log images -- shows more high values
        # in no case, do we ever scale below zero or above the max value.
        if 'Log' in Image['ImageName']:
            vmin = np.max((mean - std, 0))
            vmax = np.min((mean + 3 * std, Image['max']))
        else:
            vmin = np.max((mean - 2 * std, 0))
            vmax = np.min((mean + 2 * std, Image['max']))

        return vmin, vmax

    def DoAutoScale(self):
        CurrentImage = self.Images[self.CanvasViewSettings['CurrentImageKey']]
        CurrentImage['vlim'] = self.GetAutoScale(CurrentImage)
        self.plotImage()

    def NoteFigureZoom(self):
        self.CanvasViewSettings['xlim'] = self.axes.get_xlim()
        self.CanvasViewSettings['ylim'] = self.axes.get_ylim()
        return self.CanvasViewSettings['Shape'], self.CanvasViewSettings['xlim'], self.CanvasViewSettings['ylim']

    def WasDrawn(self, NewSize):
        self.CanvasViewSettings['xlim'] = self.axes.get_xlim()
        self.CanvasViewSettings['ylim'] = self.axes.get_ylim()
        return

    def ResetFigureZoom(self, Shape, xlim=None, ylim=None):
        # If the new image has the same dimensions, then zoom in to the same settings the user was just at.
        if Shape == self.CanvasViewSettings['Shape']:
            if (self.CanvasViewSettings['xlim'] == None) or (self.CanvasViewSettings['ylim'] == None):
                return
            if xlim == None:
                xlim = self.CanvasViewSettings['xlim']
            if ylim == None:
                ylim = self.CanvasViewSettings['ylim']
            self.axes.set_xlim(xlim)
            self.axes.set_ylim(ylim)
            self.draw()

    def MouseClicked(self, click):
        # Single clicks occur when dragging and zooming.  So double click is used to select a point.
        if click.dblclick == True:
            # Get the Z value here.
            Image = self.Images[self.CanvasViewSettings['CurrentImageKey']]
            z = Image['ImageData'][int(click.ydata + 0.5), int(click.xdata + 0.5)]
            self.MouseDblClickedCoord = (click.xdata, click.ydata, z)
            self.parent.DoubleClickEvent(self, self.MouseDblClickedCoord)
            return self.MouseDblClickedCoord

    def MouseMoved(self, event):
        if not event.inaxes:
            return
        try:
            self.DataReadout.setxy(event.xdata, event.ydata)
        except:
            pass
            # print event.xdata, event.ydata


class AboutBoxDialog(QtGui.QDialog, Ui_AboutDialog):
    def __init__(self):
        super(AboutBoxDialog, self).__init__()
        self.setupUi(self)


class Main(QtGui.QMainWindow, Ui_MultiLaueMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.setWindowIcon(QtGui.QIcon(":/Icons/Laue"))
        QtApp.setWindowIcon(QtGui.QIcon(":/Icons/Laue"))

        # Set up the matplotlib plots.
        self.canvasSumImage = MplCanvas(self, width=5, height=4, dpi=100)
        self.toolbarSumImage = NavigationToolbar(self.canvasSumImage, self.widgetMain)
        self.datareadoutSumImage = DataReadoutControl(self.canvasSumImage)
        self.comboSumImage = QtGui.QComboBox()
        self.layoutSumImage.addWidget(self.datareadoutSumImage)
        self.layoutSumImage.addWidget(self.canvasSumImage)
        self.layoutSumImage.addWidget(self.toolbarSumImage)
        self.layoutSumImage.addWidget(self.comboSumImage)
        self.canvasSumImage.AfterInitialize(self.comboSumImage, self.toolbarSumImage, self.datareadoutSumImage)

        # Set up the matplotlib plots.
        # self.widgetMain
        self.canvasSingleImage = MplCanvas(self, width=5, height=4, dpi=100)
        self.toolbarSingleImage = NavigationToolbar(self.canvasSingleImage, self.widgetMain)
        self.datareadoutSingleImage = DataReadoutControl(self.canvasSingleImage)
        self.comboSingleImage = QtGui.QComboBox()
        self.layoutSingleImage.addWidget(self.datareadoutSingleImage)
        self.layoutSingleImage.addWidget(self.canvasSingleImage)
        self.layoutSingleImage.addWidget(self.toolbarSingleImage)
        self.layoutSingleImage.addWidget(self.comboSingleImage)
        self.canvasSingleImage.AfterInitialize(self.comboSingleImage, self.toolbarSingleImage, self.datareadoutSingleImage)

        # Set up the matplotlib plots.
        self.canvasTopograph = MplCanvas(self, width=5, height=4, dpi=100)
        self.toolbarTopograph = NavigationToolbar(self.canvasTopograph, self.widgetMain)
        self.datareadoutTopograph = DataReadoutControl(self.canvasTopograph)
        self.comboTopograph = QtGui.QComboBox()
        self.layoutTopograph.addWidget(self.datareadoutTopograph)
        self.layoutTopograph.addWidget(self.canvasTopograph)
        self.layoutTopograph.addWidget(self.toolbarTopograph)
        self.layoutTopograph.addWidget(self.comboTopograph)
        self.canvasTopograph.AfterInitialize(self.comboTopograph, self.toolbarTopograph, self.datareadoutTopograph)

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

        # Tell the canvases and Readouts to update.
        self.datareadoutSingleImage.setxy(0, 0)
        self.datareadoutSumImage.setxy(0, 0)
        self.datareadoutTopograph.setxy(0, 0)

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
        # Clear all the images.
        # self.comboSumImage.clear()
        # self.comboTopograph.clear()
        # self.comboSingleImage.clear()
        self.canvasSumImage.InitCanvasData()
        self.canvasTopograph.InitCanvasData()
        self.canvasSingleImage.InitCanvasData()
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

            def AddOne(Images, Scan, Key, ImageName):
                # When making an OrderedDict of images, (each containing an OrderedDict) then we want a simple one line add to dictionary.
                Images[Key] = OrderedDict()
                Images[Key]['ImageData'] = Scan[Key][:]
                Images[Key]['ImageName'] = ImageName

            # Make an images data structure which will have the images from the scan.
            Images = OrderedDict()

            # Populate the combobox for the sum image with whatever sum images are in the scan.
            if 'StDevLogImage' in Scan:
                AddOne(Images, Scan, Key='StDevLogImage', ImageName='StDev Image Logarithmic')
            if 'StDevImage' in Scan:
                AddOne(Images, Scan, Key='StDevImage', ImageName='StDev Image')
            if 'SumLogImage' in Scan:
                AddOne(Images, Scan, Key='SumLogImage', ImageName='Sum Image Logarithmic')
            if 'SumImage' in Scan:
                AddOne(Images, Scan, Key='SumImage', ImageName='Sum Image')

            # Now init the sum image canvas with this data (it will init the combobox too.)
            self.canvasSumImage.InitCanvasData(Images)

            try:
                # Select the image the user was last looking at by "clicking" the appropriate combo box line.  It will sync with the canvas.
                self.comboSumImage.setCurrentIndex(self.comboSumImage.findData(self.Defaults['comboSumImageLastValue']))
            except:
                self.comboSumImage.setCurrentIndex(0)

    def SaveAggregateImage(self, FileName=None):
        if FileName is None or FileName == False:
            # Set the default filename to the type of image (SumImage, etc...)
            FileName = os.path.join(self.Defaults['DefaultFileDialogDir'],
                                    str((self.comboSumImage.itemData(self.comboSumImage.currentIndex()).toString()) + '.tif'))
            Opts = QtGui.QFileDialog.Option(0x40)  # QtGui.QFileDialog.HideNameFilterDetails
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
            FileName = os.path.join(self.Defaults['DefaultFileDialogDir'],
                                    str(self.comboTopograph.itemData(self.comboTopograph.currentIndex()).toString()) + '.tif')
            Opts = QtGui.QFileDialog.Option(0x40)  # QtGui.QFileDialog.HideNameFilterDetails
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
            FileName = os.path.join(self.Defaults['DefaultFileDialogDir'],
                                    str(self.comboSingleImage.itemData(self.comboSingleImage.currentIndex()).toString()) + '.tif')
            Opts = QtGui.QFileDialog.Option(0x40)  # QtGui.QFileDialog.HideNameFilterDetails
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
            FileName = os.path.join(self.Defaults['DefaultFileDialogDir'], self.Scan.attrs['ScanName'] + '_.tif')
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
        FileName = QtGui.QFileDialog.getOpenFileName(self, caption='Open Scan configuration file.', directory=FileName,
                                                     filter='JSON files (*.json);;All files (*.*)')

        if FileName != '':
            PathName, FileName = os.path.split(str(FileName))
            self.Defaults['DefaultFileDialogDir'] = PathName

            # The import can be many minutes long, so spin this off into a thread.
            self.ImportThread = ImportScanThread(FileName, PathName, "StatusFunc(PyQt_PyObject)")
            # ImportScan(FileName, PathName, self.StatusFunc)

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
        # Note the current zoom settings.
        shape, xlim, ylim = self.canvasSumImage.NoteFigureZoom()
        WhichImage = str(self.comboSumImage.itemData(self.comboSumImage.currentIndex()).toString())
        if WhichImage == '':
            return
        self.canvasSumImage.SetCurrentImage(WhichImage)
        self.Defaults['comboSumImageLastValue'] = WhichImage
        # Put the zoom back
        self.canvasSumImage.ResetFigureZoom(shape, xlim, ylim)

    def comboTopograph_Changed(self):
        # Note the current zoom settings.
        shape, xlim, ylim = self.canvasTopograph.NoteFigureZoom()
        WhichImage = str(self.comboTopograph.itemData(self.comboTopograph.currentIndex()).toString())
        if WhichImage == '':
            return
        self.canvasTopograph.SetCurrentImage(WhichImage)
        self.Defaults['comboTopographLastValue'] = WhichImage
        # Put the zoom back
        self.canvasTopograph.ResetFigureZoom(shape, xlim, ylim)

    def comboSingleImage_Changed(self):
        # Note the current zoom settings.
        shape, xlim, ylim = self.canvasSingleImage.NoteFigureZoom()

        # Now switch the image to the one just selected.
        WhichImage = str(self.comboSingleImage.itemData(self.comboSingleImage.currentIndex()).toString())
        if WhichImage == '':
            return
        # if WhichImage == 'Linear':
        #     self.canvasSingleImage.setImageData(self.SingleImageRawData)
        # if WhichImage == 'Logarithmic':
        #     self.canvasSingleImage.setImageData(BasicProcessing.CleanLog(self.SingleImageRawData))
        # if WhichImage == 'Energy':
        #     self.canvasSingleImage.setImageData(self.EnergyImageRawData)
        # if WhichImage == 'EnergyFit':
        #     self.canvasSingleImage.setImageData(self.EnergyFitImageRawData)
        self.canvasSingleImage.SetCurrentImage(WhichImage)
        self.Defaults['comboSingleImageLastValue'] = WhichImage
        # Put the zoom back
        self.canvasSingleImage.ResetFigureZoom(shape, xlim, ylim)

    def StatusFunc(self, StatusStr):
        # The status is ALWAYS written to the status bar.
        self.statusBar.showMessage(StatusStr)

    def DoubleClickEvent(self, Canvas, Coord):
        self.statusBar.showMessage('Selected: (x,y)=(%d,%d), value=%g' % Coord)
        # If the sum image was clicked, then that means we need to turn that pixel or region into a topograph.
        if Canvas == self.canvasSumImage:
            # Note the current zoom settings of the topograph image canvas.
            shape, xlim, ylim = self.canvasTopograph.NoteFigureZoom()

            # Make the topograph.
            self.statusBar.showMessage('Generating topograph from coordinate (x,y)=(%d,%d)...' % Coord[0:2])
            Topo = BasicProcessing.MakeTopographFromCoordinate(self.Scan, Coord)

            Images = OrderedDict()
            # Populate the topograph canvas with the log and linear topographs.
            Images['TopographLog'] = OrderedDict()
            Images['TopographLog']['ImageData'] = BasicProcessing.CleanLog(Topo)
            Images['TopographLog']['ImageName'] = 'Topopgraph Logarithmic'
            Images['Topograph'] = OrderedDict()
            Images['Topograph']['ImageData'] = Topo
            Images['Topograph']['ImageName'] = 'Topopgraph Linear'

            # Now init the sum image canvas with this data (it will init the combobox too.)
            self.canvasTopograph.InitCanvasData(Images)

            # And select the last option selected by the user or nothing if it doesn't exist.
            try:
                self.comboTopograph.setCurrentIndex(self.comboTopograph.findData(self.Defaults['comboTopographLastValue']))
            except:
                self.comboTopograph.setCurrentIndex(0)
            # Put the zoom back
            self.canvasTopograph.ResetFigureZoom(shape, xlim=xlim, ylim=ylim)
            self.statusBar.showMessage('Generated topograph from coordinate (x,y)=(%d,%d)' % Coord[0:2])

        if Canvas == self.canvasTopograph:
            # Note the current zoom settings of the single image canvas.
            shape, xlim, ylim = self.canvasSingleImage.NoteFigureZoom()

            # If the user clicked on a topograph pixel, then get the diffraction pattern from that pixel.
            SingleImage, EnergyImage, EnergyFitImage = BasicProcessing.GetSingleImageFromTopographCoordinate(self.Scan, Coord)
            # self.SingleImageRawData = SingleImage
            # self.EnergyImageRawData = EnergyImage
            # self.EnergyFitImageRawData = EnergyFitImage

            # Make an ordered dict of ordered dicts -- one for each image, and populate the canvas with them.
            Images = OrderedDict()
            if self.Scan.attrs['ScanType'] == 'MultiLaue':
                Images['Energy'] = OrderedDict({'ImageData': EnergyImage, 'ImageName': 'Energy'})
                Images['EnergyFit'] = OrderedDict({'ImageData': EnergyFitImage, 'ImageName': 'Energy Fit'})
                Images['Logarithmic'] = OrderedDict({'ImageData': BasicProcessing.CleanLog(SingleImage), 'ImageName': 'Laue Logarithmic'})
                Images['Linear'] = OrderedDict({'ImageData': SingleImage, 'ImageName': 'Laue Linear'})
            else:
                Images['Logarithmic'] = OrderedDict({'ImageData': BasicProcessing.CleanLog(SingleImage), 'ImageName': 'Laue Logarithmic'})
                Images['Linear'] = OrderedDict({'ImageData': SingleImage, 'ImageName': 'Laue Linear'})
            self.canvasSingleImage.InitCanvasData(Images)

            try:
                # Select the image the user was last looking at by "clicking" the appropriate combo box line.  It will sync with the canvas.
                self.comboSingleImage.setCurrentIndex(self.comboSingleImage.findData(self.Defaults['comboSingleImageLastValue']))
            except:
                self.comboSingleImage.setCurrentIndex(0)

            # Put the zoom back
            self.canvasSingleImage.ResetFigureZoom(shape, xlim=xlim, ylim=ylim)

            self.statusBar.showMessage('Picked single image from topograph from coordinate (x,y)=(%d,%d)' % Coord[0:2])
        if Canvas == self.canvasSingleImage:
            print "Single Image Click not implemented."


if __name__ == '__main__':
    QtApp = QtGui.QApplication(sys.argv)
    QtApp.setApplicationName('MultiLaue')

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
