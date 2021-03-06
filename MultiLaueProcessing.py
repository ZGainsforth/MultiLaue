# Created 2016, Zack Gainsforth

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
import PhysicsBasics as pb
import h5py
import multiprocessing
import time
from AbsorptionCorrection import DoAbsorptionFilter, CorrectDetectorProperties
from multiprocessing import Pool
from BasicProcessing import LoadScan
from PyQt5 import QtGui, QtCore

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

# If there are fewer counts in the pixels than this number, then we won't compute an energy for that spot.  This saves
# computation time and results in more useful images (since they don't have a bunch of noisy "computed" pixels.
StatisticallySignificantCountsThreshhold = 2500

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
        NormalizedCurve = CorrectDetectorProperties(E, NormalizedCurve, 50, 50, 0.001, 0.001, 350, 0.001)  # This should improve things, but right now the filter thicknesses are calibrated without it.
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

    assert (len(I) == BeamlineRatioSpectra.shape[0]), "I vector must have the same number of values as there are beamline ratio spectra."

    # Now compute the ratio intensities measured.
    Iratio = I.copy().astype('float')
    Iratio[:] /= Iratio[0]
    if not quiet:
        print(Iratio)

    # And compare them against the apparent intensity ratio curves.
    RatioComparison = Iratio[:,np.newaxis]-BeamlineRatioSpectra
    FitVal = np.std(RatioComparison, axis=0)
    if not quiet:
        plt.figure()
        plt.plot(E, FitVal)
        plt.hold(True)
        print(RatioComparison.shape)
        for i in range(len(I)):
            plt.plot(E, RatioComparison[i,:])
        plt.title('Fit energy')
        plt.legend(['Best Fit'] + [str(i) for i in range(len(I))])

        # Print the best fit energy
        print("Best fit energy is %g eV with fit value %g" % (E[np.argmin(FitVal)], FitVal[np.argmin(FitVal)]))

    ind = np.argmin(FitVal)
    return E[ind], FitVal[ind]

def ComputeEnergyImage(I, BeamlineApparentRatioSpectra):

    # Make a numpy array for the energy image and the fit image.  When they are done, we plunk them into the HDF5.
    EVec = np.zeros(I.shape[0:2])
    FitVec = np.zeros(I.shape[0:2])

    for m in range(I.shape[0]):
        for n in range(I.shape[1]):
            # Skip this pixel if any of the filtered images has too few counts to produce a good fit.
            if np.min(I[m, n, :]) < StatisticallySignificantCountsThreshhold:
                continue
            EVec[m,n], FitVec[m,n] = ComputeSpotEnergy(I[m, n, :], BeamlineApparentRatioSpectra)

    return EVec, FitVec

def MakeMultiLaueEnergyCube(Scan, StatusFunc=None):

    assert Scan.attrs['ScanType'] == 'MultiLaue', 'Can only make an energy cube from a MultiLaue.'

    Cube = Scan['DataCube']

    # Remove any datasets we are going to compute in case we are recomputing.
    for k in list(Scan.keys()):
        if k in ['EnergyCube', 'EnergyFitValCube', 'BeamlineFluxEnergies', 'BeamlineFlux', 'BeamlineFilteredSpectra', 'BeamlineApparentSpectra', 'BeamlineApparentRatioSpectra']:
            del Scan[k]

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

    # Get the Beamline flux apparent spectra and store them in the HDF5.
    BeamlineFilteredSpectra, BeamlineApparentSpectra, BeamlineApparentRatioSpectra = ComputeAbsorbedBeamlineFlux(WtPcts, FilterDensities, FilterThicknesses, NumPositions)
    #Scan.create_dataset('FluxEnergies', E.shape)
    Scan['BeamlineFluxEnergies'] = E
    #Scan.create_dataset('BeamlineFlux', E.shape)
    Scan['BeamlineFlux'] = Flux
    #Scan.create_dataset('BeamlineFilteredSpectra', E.shape)
    Scan['BeamlineFilteredSpectra'] = BeamlineFilteredSpectra
    #Scan.create_dataset('BeamlineApparentSpectra', E.shape)
    Scan['BeamlineApparentSpectra'] = BeamlineApparentSpectra
    #Scan.create_dataset('BeamlineApparentRatioSpectra', E.shape)
    Scan['BeamlineApparentRatioSpectra'] = BeamlineApparentRatioSpectra

    # Create an array (same size as one row in the topograph) to contain the results passed back by the multiprocessing.
    # Multiprocessing will do one row of the topograph at a time.
    Result = np.ndarray((Cube.shape[0]), dtype=object)

    for y in range(Cube.shape[1]):

        p = Pool()

        StatusStr = "Energy image: line %d, Pixels # %d-%d of %d (this may take a few minutes)" % (
        y, y * Cube.shape[0] + 1, (y+1) * Cube.shape[0], Cube.shape[0] * Cube.shape[1])
        if StatusFunc is not None:
            StatusFunc(StatusStr)
        else:
            print(StatusStr)

        for x in range(Cube.shape[0]):
            # Get all the Laues for this image from the HDF5 at once.
            I = Cube[x, y, :, :, :]

            # Compute one Energy image and its fit image.
            Result[x] = p.apply_async(ComputeEnergyImage, [I, BeamlineApparentRatioSpectra])

        # After one row of pixels, close down the asynchronous pool and let it process those.
        p.close()
        p.join()

        # Stash the results from that multiprocess pool into the HDF5 file and we'll go around for the next line.
        for x in range(Cube.shape[0]):
            EnergyCube[x, y, :, :], EnergyFitValCube[x, y, :, :] = Result[x].get()

    return


class ProcessMultiLaueThread(QtCore.QThread):
    StatusSignal = QtCore.pyqtSignal(object)

    def __init__(self, FileName):
        QtCore.QThread.__init__(self)
        self.FileName = FileName

    def run(self):
        f, Scan = LoadScan(self.FileName, readwrite=True)
        self.StatusFunc('Opened ' + Scan.attrs['ScanName'] + '.')

        MakeMultiLaueEnergyCube(Scan, self.StatusFunc)
        f.close()
        self.StatusFunc('MultiLaue processing complete.')

    def StatusFunc(self, StatusStr):
        if self.StatusSignal is not None:
            self.StatusSignal.emit(StatusStr)
            #self.emit(QtCore.SIGNAL(self.StatusSignal), StatusStr)
        else:
            print(StatusStr)

def TestAgainstSilicon():
    # Reflection (-3,3,-3) with energy 8.44862 has intensities:
    # No filter:     108708
    # One filter:    79690.7
    # Two filters:   57407.9
    # Three filters: 37413.6
    #I = np.array([108708, 79690, 57407, 37413]) # Observed energies.
    #I = np.array([ 108708.,   79690.,   57916.,   42499.]) # back computed from jump values.

    # Reflection (-2,4,-2) with energy 12.4727 has intensities:
    # No filter:     175932
    # One filter:    147997
    # Two filters:   116348
    # Three filters: 70706
    #I = np.array([175932, 147997, 116348, 70706]) # Observed energies.
    #I = np.array([179167, 145417, 112917, 87084]) # back computed from jumps.

    # Reflection (-5,5,-3) with energy 15.6641 has intensities:
    # No filter:     71846.3
    # One filter:    63194.4
    # Two filters:   54027.5
    # Three filters: 43934
    #I = np.array([71846, 63194, 54027, 43934]) # Observed energies. #(from ignoring the slopes)
    #I = np.array([71080, 63261, 56302, 50109]) # Observed energies. # using only the discontinuities

    hkls = np.array([ [-2 ,    4 ,   -2],
                      [-3 ,    3 ,   -1],
                      [-4 ,    2 ,   -2],
                      [-3 ,    3 ,   -3],
                      [-5 ,    3 ,   -1],
                      [-6 ,    4 ,   -2],
                      [-3 ,    5 ,   -3],
                      [-6 ,    6 ,   -4],
                      [-5 ,    5 ,   -3],
                      [-5 ,    3 ,   -3],
                      [-4 ,    6 ,   -6],
                      [-3 ,    5 ,   -5],
                      [-3 ,    7 ,   -5],
                      [-7 ,    5 ,   -3],
                      [-6 ,    8 ,   -6],
                      [-5 ,    7 ,   -5],
                      [-8 ,    6 ,   -6],
                      [-3 ,    5 ,   -7],
                      [-6 ,    6 ,   -8],
                      [-9 ,    5 ,   -3],
                      [-7 ,    5 ,   -5],
                      [-3 ,    7 ,   -7],
                      [-5 ,    7 ,   -7],
                      [-10,     6,    -8],
                      [-6 ,    8 ,  -10],
                      [-9 ,    5 ,   -5],
                      [-3 ,    7 ,   -9],
                      [-9 ,    5 ,   -7],
                      [-5 ,    7 ,   -9],
                      [-9 ,    7 ,   -7],
                      [-7 ,    7 ,   -9],
                      [-11,     5,    -7],
                      ])
    TableEperfect = list()
    TableEfit = list()
    TableEError = list()
    TableRelError = list()

    for hkl in hkls: #np.array([[-5 ,    3 ,   -3]]): #hkls:
        # Now we just compute directly from the hkl.
        (I, Eperfect) = PlotValues(hkl, quiet=True)

        #t = np.array([0, 100, 200, 300]) # Thickness with 0-3 slips each 100 um thick.
        t = np.array([0, 112, 222, 334]) # Thickness with 0-3 slips each 100 um thick.
        rho = 2.2 # g/cm3
        WtPct = np.zeros(pb.MAXELEMENT)
        WtPct[pb.Si-1] = 46.74
        WtPct[pb.O-1] = 53.26
        Efit = ComputeSpotEnergy(I, WtPct, rho, t, quiet=True)

        Eerror = np.abs(Efit - Eperfect)
        RelError = np.abs(Efit - Eperfect) / Eperfect * 100
        print("Error in energy is %g.  Relative error is %0.02f percent" % (Eerror, RelError))

        TableEperfect.append(Eperfect)
        TableEfit.append(Efit)
        TableEError.append(Eerror)
        TableRelError.append(RelError)

    # Now these are populated to switch to numpy.
    TableEperfect = np.array(TableEperfect) / 1000 # Convert eV to keV.
    TableEfit = np.array(TableEfit) / 1000
    TableEError = np.array(TableEError)
    TableRelError = np.array(TableRelError)

    # Show a final figure comparing the errors against the flux curve.  Publication quality!
    FluxCurve = np.genfromtxt('../Beamline Characteristics/whitebeamflux.txt', skip_header=1)
    FluxCurve[:,1] /= max(FluxCurve[:,1])/35
    FluxCurve[:,0] /= 1000 # Switch to keV from eV.

    fig, ax = QuickPlot.SpecPlot(FluxCurve, boldlevel=3, title='Flux curve compared with errors', xlabel='keV', ylabel='Points: % relative error\nCurve: flux (arbitrary units)')
    QuickPlot.QuickPlot(TableEperfect,TableRelError, figax=(fig,ax), plottype='scatter', boldlevel=5)
    plt.legend(['Flux Curve', 'Error of best fit values'])

    print(("%% rel error mean = %0.02f and standard deviation: %0.02f" % (np.mean(TableRelError), np.std(TableRelError))))

    print(TableEfit)
    Keepers = (TableEfit>11) & (TableEfit<21)
    print(Keepers)

    print(("%% rel error mean = %0.02f and standard deviation: %0.02f in region 11-21 keV" % (np.mean(TableRelError[Keepers]), np.std(TableRelError[Keepers]))))

    def raise_window(figname=None):
        if figname: plt.figure(figname)
        cfm = plt.get_current_fig_manager()
        cfm.window.activateWindow()
        cfm.window.raise_()

    raise_window()
    plt.show()

if __name__ == '__main__':

    TestAgainstSilicon()

    # quiet = False
    # tStart = time.time()
    # #f, Scan = LoadScan('GRA95229_mLaue_7.hdf5', readwrite=True)
    # #f, Scan = LoadScan('GRA95229_mLaue2.hdf5', readwrite=True)
    # f, Scan = LoadScan('Si Hyperlaue/SiHyperlaueFinal_Shielded_Extract.hdf5', readwrite=True)
    # EnergyCube = MakeMultiLaueEnergyCube(Scan)
    # #Scan.create_dataset('EnergyCube', data=EnergyCube)
    # f.close()
    # print time.time() - tStart

