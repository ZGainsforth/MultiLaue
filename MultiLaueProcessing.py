# Created 2016, Zack Gainsforth
from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
import PhysicsBasics as pb
import h5py
import multiprocessing
import time
from AbsorptionCorrection import DoAbsorptionFilter
from multiprocessing import Pool
from BasicProcessing import LoadScan
from PyQt4 import QtGui, QtCore

### Initialization code for MultiLaue

# Energy axis for the experiment
E = np.arange(2000,26001, 10) # 2 keV to 26 keV in 10 eV steps.

# Get the beamline Flux curve.
# Fraw = np.genfromtxt('../Beamline Characteristics/12.3.2_flux_after extrapolated.txt')
Fraw = np.genfromtxt('Beamline Characteristics/whitebeamflux.txt', skip_header=1)
Fraw[:,1] /= max(Fraw[:,1])
F = interp1d(Fraw[:,0], Fraw[:,1], bounds_error=False, fill_value=0)
Flux = F(E)
Flux /= max(Flux)

# For debug, quiet = False.  Set True for live time and it won't print out plots showing the algorithm progressing.
quiet = True

def ComputeAbsorbedBeamlineFlux(WtPct, rho, t, NumFilters):

    assert (WtPct.shape[0] == NumFilters), "WtPct must have the same dimension as there are filter positions."
    assert (len(rho) == NumFilters), "rho must have the same dimension as there are filter positions."
    assert (len(t) == NumFilters), "t must have the same dimension as there are filter positions."

    # Compute the absorption through each of the filters.  These don't take into account harmonics yet.
    FilteredSpectrum = list()
    #FilteredSpectrum.append(np.ones(len(E))*Flux)     # The first index is no filter.

    for n in range(len(t)):
        #First just get the absorption as a function of energy for incident intensity of 1.
        NormalizedCurve = DoAbsorptionFilter(E, Iin=1, WtPct=WtPct[n,:], rho=rho[n], AbsorptionLength=t[n])
        #NormalizedCurve = CorrectDetectorProperties(E, NormalizedCurve, 50, 50, 0.001, 0.001, 350, 0.001)  # This should improve things, but right now the filter thicknesses are calibrated without it.
        # Multiply that by the flux of the incident beam to get the actual light spectrum hitting the sample through each filter.
        FilteredSpectrum.append(NormalizedCurve*Flux)

    # Show the absorption curves.
    if not quiet:
        plt.figure()
        for i in range(len(t)):
            plt.plot(E,FilteredSpectrum[i])
            plt.hold(True)
        plt.legend([str(i) for i in range(len(t))])
        plt.title('Absorption curves relative to intensity = 1')

    # Now compute the apparent intensity of light for each reflection with a d-spacing having a specific energy.
    # Because of harmonics, it won't be just the incident spectrum.  Lower energies cannot excite reflections that need higher energies,
    # but higher harmonics can excite lower.
    # Make an array holding the final apparent spectrum which will have one complete energy axis for each filter.
    ApparentSpectrum = np.zeros([len(t), len(E)])
    # The outer loop is once for each filtered spectrum.
    for i in range(len(t)):

        # Note what the incident light spectrum coming out of the filter is.
        k = FilteredSpectrum[i]

        # The inner loop convolves the spectrum with its own harmonics to get an apparent spectrum.  I.e. how intense the reflection at that energy will be.
        NumHarmonics = 2
        for j, Energy in enumerate(E):
            # Get the index of the 2*E, 3*E, ... harmonics.
            for n in range(NumHarmonics):
                jn = (np.abs(E-(n+1)*Energy)).argmin()
                ApparentSpectrum[i,j] += k[jn]

    # Show the Apparent intensity curves.
    if not quiet:
        plt.figure()
        for i in range(len(t)):
            plt.plot(E, ApparentSpectrum[i,:])
            plt.hold(True)
        plt.legend([str(i) for i in range(len(t))])
        plt.title('Absorption curves relative to intensity = 1, with harmonics')

    # At some energy, the ratio of apparent intensities should be the same as the ratios of the measured intensities.
    # That energy will be the right one.  Make new ratio intensities, where each curve is ratioed to the unfiltered curve.
    ApparentRatioSpectrum = ApparentSpectrum.copy()
    for i in range(1, len(t)):
        ApparentRatioSpectrum[i, :] /= ApparentRatioSpectrum[0, :]
    # And don't forget to set the first spectrum to intensity of 1:
    ApparentRatioSpectrum[0, :] = 1

    # Show the Apparent intensity ratio curves.
    if not quiet:
        plt.figure()
        for i in range(len(t)):
            plt.plot(E, ApparentRatioSpectrum[i, :])
            plt.hold(True)
        plt.legend([str(i) for i in range(len(t))])
        plt.title('Absorption curves relative to intensity = 1, with harmonics\nNormalized to the unfiltered spectrum')

    return FilteredSpectrum, ApparentSpectrum, ApparentRatioSpectrum

def ComputeSpotEnergy(I, BeamlineRatioSpectra):
    # I is a numpy array with I0, I1, I2, etc. where I1+ are the filtered intensities.
    # WtPct is the filter composition. (It is assumed that all filters have the same composition.
    # rho is the filter density (g/cm3) it is assumed that all filters have the same density.
    # t is the thickness of the filters -- it should have the same length as I.

    assert (len(I) == BeamlineRatioSpectra.shape[0]), "I must same number of intensities as beamline ratio spectra."

    # Now compute the ratio intensities measured.
    Iratio = I.copy().astype('float')
    Iratio[:] /= Iratio[0]
    if not quiet:
        print Iratio

    # And compare them against the apparent intensity ratio curves.
    RatioComparison = Iratio[:,np.newaxis]-BeamlineRatioSpectra
    FitVal = np.std(RatioComparison, axis=0)
    if not quiet:
        plt.figure()
        plt.plot(E, FitVal)
        plt.hold(True)
        print RatioComparison.shape
        for i in range(len(I)):
            plt.plot(E, RatioComparison[i,:])
        plt.title('Fit energy')
        plt.legend(['Best Fit'] + [str(i) for i in range(len(I))])

        # Print the best fit energy
        print "Best fit energy is %g eV with fit value %g" % (E[np.argmin(FitVal)], FitVal[np.argmin(FitVal)])

    ind = np.argmin(FitVal)
    return E[ind], FitVal[ind]

def ComputeEnergyImageSlow(I, BeamlineRatioSpectra):
    # I is a numpy array with I0, I1, I2, etc. where I1+ are the filtered intensities.
    # WtPct is the filter composition. (It is assumed that all filters have the same composition.
    # rho is the filter density (g/cm3) it is assumed that all filters have the same density.
    # t is the thickness of the filters -- it should have the same length as I.

    assert (I.shape[-1] == BeamlineRatioSpectra.shape[0]), "I have the same number of images as beamline ratio spectra."

    NumFrames = I.shape[-1]

    # Now compute the ratio intensities measured.
    Iratio = I.copy().astype('float')
    # Ratio each frame to the first...
    for n in range(1, NumFrames):
        Iratio[:, :, n] /= Iratio[:, :, 0]
    # ... and set the first to unity.
    Iratio[:, :, 0] = 1
    if not quiet:
        print Iratio

    EImage = np.zeros((I.shape[0], I.shape[1]))
    FitImage = np.zeros((I.shape[0], I.shape[1]))

    for m in range(I.shape[0]):
        print m
        # And compare them against the apparent intensity ratio curves.
        # Shape of RatioComparison is one row of the image x number of filters x number of energies.
        RatioComparison = Iratio[m, :, :, np.newaxis]-BeamlineRatioSpectra
        FitVal = np.std(RatioComparison, axis=1)
        # if not quiet:
        #     plt.figure()
        #     plt.plot(E, FitVal)
        #     plt.hold(True)
        #     print RatioComparison.shape
        #     for i in range(len(I)):
        #         plt.plot(E, RatioComparison[i,:])
        #     plt.title('Fit energy')
        #     plt.legend(['Best Fit'] + [str(i) for i in range(len(I))])
        #
        #     # Print the best fit energy
        #     print "Best fit energy is %g eV with fit value %g" % (E[np.argmin(FitVal)], FitVal[np.argmin(FitVal)])

        inds = np.argmin(FitVal, axis=-1)
        EImage[m,:] = E[inds]
        FitImage[m,:] = np.diag(FitVal[:,inds])

    return EImage, FitImage

def ComputeEnergyImage(I, BeamlineApparentRatioSpectra, x):

    # Make a numpy array for the energy image and the fit image.  When they are done, we plunk them into the HDF5.
    EVec = np.zeros(I.shape[0:2])
    FitVec = np.zeros(I.shape[0:2])

    for m in range(I.shape[0]):
        #print x,m
        for n in range(I.shape[1]):
            EVec[m,n], FitVec[m,n] = ComputeSpotEnergy(I[m, n, :], BeamlineApparentRatioSpectra)

    return EVec, FitVec

def MakeMultiLaueEnergyCube(Scan, StatusFunc=None):

    assert Scan.attrs['ScanType'] == 'MultiLaue', 'Can only make an energy cube from a MultiLaue.'

    Cube = Scan['DataCube']

    # If the energy cube or energy fit val cubes exist, then nuke them so we can recompute.
    if 'EnergyCube' in Scan:
        del Scan['EnergyCube']
    if 'EnergyFitValCube' in Scan:
        del Scan['EnergyFitValCube']

    # The shape of the energy cube is the same as the shape of the Cube, minus the last (filter) dimension.
    EnergyCubeShape = Cube.shape[0:4]
    EnergyCube = Scan.create_dataset('EnergyCube', shape=EnergyCubeShape, dtype='float32', chunks=(1, 1, 200, 200), compression='gzip')
    # We also make a cube which has how good the fit was so we don't trust energies that are no good.
    EnergyFitValCube = Scan.create_dataset('EnergyFitValCube', shape=EnergyCubeShape, dtype='float32', chunks=(1, 1, 200, 200), compression='gzip')

    # Compute how many pixels total.
    NumImages = np.array(Cube.shape)[[0, 1]].prod()
    n = 1  # Starting with the first image.

    # Get the filter information from the data cube.
    WtPcts = Scan['Filter']['FilterWtPcts'][:]
    FilterDensities = Scan['Filter'].attrs['FilterDensities']
    FilterThicknesses = Scan['Filter'].attrs['FilterThicknesses']
    NumPositions = Scan['Filter'].attrs['NumberOfPositions']

    BeamlineFilteredSpectra, BeamlineApparentSpectra, BeamlineApparentRatioSpectra = ComputeAbsorbedBeamlineFlux(WtPcts, FilterDensities, FilterThicknesses, NumPositions)

    # # Make a temp numpy array for the energy image and the fit image.  When they are done, we plunk them into the HDF5.
    # EVec = np.zeros((Cube.shape[2], Cube.shape[3]))
    # FitVec = np.zeros((Cube.shape[2], Cube.shape[3]))
    # Create an array (same size as one row in the topograph) to contain the results passed back by the multiprocessing.
    # Multiprocessing will do one row of the topograph at a time.
    Result = np.ndarray((Cube.shape[0]), dtype=object)

    for y in range(Cube.shape[1]):

        p = Pool()

        StatusStr = "Energy image: line %d, Pixels # %d-%d of %d (this may take a few minutes)" % (
        y, y * Cube.shape[0] + 1, (y+1) * Cube.shape[0] + 1, Cube.shape[0] * Cube.shape[1])
        if StatusFunc is not None:
            StatusFunc(StatusStr)
        else:
            print StatusStr

        for x in range(Cube.shape[0]):

            # Compute one Energy image and its fit image.

            # Get all the Laues for this image from the HDF5 at once.
            I = Cube[x, y, :, :, :]
            # EVec, FitVec = ComputeEnergyImage(I, BeamlineApparentRatioSpectra)

            # for m in range(Cube.shape[2]):
            #     print m
            #     for n in range(Cube.shape[3]):
            #         EVec[m,n], FitVec[m,n] = ComputeSpotEnergy(I[m, n, :], BeamlineApparentRatioSpectra)

            Result[x] = p.apply_async(ComputeEnergyImage, [I, BeamlineApparentRatioSpectra, x])
            #ComputeEnergyImage(I, BeamlineApparentRatioSpectra, x)

            # for m in range(Cube.shape[2]):
            #     print m
            #     for n in range(Cube.shape[3]):
            #         EVec[m,n], FitVec[m,n] = Result[m,n].get()
            #
            # # Fill out this frame in the HDF5 cubes.
            # EnergyCube[x, y, :, :] = EVec
            # EnergyFitValCube[x, y, :, :] = FitVec
            # break

        p.close()
        p.join()

        # Read the results from that multiprocess pool into the HDF5 file and we'll go around for the next line.
        for x in range(Cube.shape[0]):
            EnergyCube[x, y, :, :], EnergyFitValCube[x, y, :, :] = Result[x].get()


    return


class ProcessMultiLaueThread(QtCore.QThread):

    def __init__(self, FileName, StatusSignal=None):
        QtCore.QThread.__init__(self)
        self.FileName = FileName
        self.StatusSignal = StatusSignal

    def run(self):
        f, Scan = LoadScan(self.FileName, readwrite=True)
        self.StatusFunc('Opened ' + Scan.attrs['ScanName'] + '.')

        EnergyCube = MakeMultiLaueEnergyCube(Scan, self.StatusFunc)
        f.close()

    def StatusFunc(self, StatusStr):
        if self.StatusSignal is not None:
            self.emit(QtCore.SIGNAL(self.StatusSignal), StatusStr)
        else:
            print StatusStr


        # if self.StatusFunc is not None:
        #     self.StatusFunc('Multilaue processing complete')
        # else:
        #     print 'Multilaue processing complete'


# def ProcessMultiLaue(FileName, StatusFunc=None):
#
#     # Set up a timer which will keep the GUI responsive for the user
#     t = QtCore.QTimer()
#     t.timeout.connect(KeepQtAlive)
#     t.start(1000)
#
#     f, Scan = LoadScan(FileName, readwrite=True)
#     if StatusFunc is not None:
#         StatusFunc('Opened ' + Scan.attrs['ScanName'] + '.')
#     else:
#         print 'Opened ' + Scan.attrs['ScanName'] + '.'
#
#     EnergyCube = MakeMultiLaueEnergyCube(Scan, StatusFunc)
#     f.close()
#
#     if StatusFunc is not None:
#         StatusFunc('Multilaue processing complete')
#     else:
#         print 'Multilaue processing complete'
#
#     t.stop()
#
# def KeepQtAlive():
#     print 'KeepQtAlive!'
#     QtGui.QApplication.processEvents()

if __name__ == '__main__':

    tStart = time.time()
    #f, Scan = LoadScan('GRA95229_mLaue_7.hdf5', readwrite=True)
    f, Scan = LoadScan('GRA95229_mLaue2.hdf5', readwrite=True)
    EnergyCube = MakeMultiLaueEnergyCube(Scan)
    #Scan.create_dataset('EnergyCube', data=EnergyCube)
    f.close()

    print time.time() - tStart
