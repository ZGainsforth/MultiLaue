# Created 2016, Zack Gainsforth
from __future__ import division
# import matplotlib
# matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
import QuickPlot
import PhysicsBasics as pb
from PlotValues import PlotValues
from matplotlib.pyplot import ion

# ion()

# import matplotlib.pylab as pylab
# pylab.rcParams['figure.figsize'] = 8, 8  # that's default image size for this interactive session

from AbsorptionCorrection import DoAbsorptionFilter, CorrectDetectorProperties

### Initialization code

# Energy axis for the experiment
E = np.arange(2000, 26001, 10)  # 2 keV to 26 keV in 10 eV steps.

# Get the beamline Flux curve.
# Fraw = np.genfromtxt('../Beamline Characteristics/12.3.2_flux_after extrapolated.txt')
Fraw = np.genfromtxt('../Beamline Characteristics/whitebeamflux.txt', skip_header=1)
Fraw[:, 1] /= max(Fraw[:, 1])
F = interp1d(Fraw[:, 0], Fraw[:, 1], bounds_error=False, fill_value=0)
Flux = F(E)
Flux /= max(Flux)


def ComputeSpotEnergy(I, WtPct, rho, t, quiet=False):
    # I is a numpy array with I0, I1, I2, etc. where I1+ are the filtered intensities.
    # WtPct is the filter composition. (It is assumed that all filters have the same composition.
    # rho is the filter density (g/cm3) it is assumed that all filters have the same density.
    # t is the thickness of the filters -- it should have the same length as I.

    assert (len(t) == len(I)), "I and t must have the same length."

    # Compute the absorption through each of the filters.  These don't take into account harmonics yet.
    FilteredSpectrum = list()
    FilteredSpectrum.append(np.ones(len(E)) * Flux)  # The first index is no filter.
    for n in range(1, len(t)):  # Skip the first index which is unabsorbed.
        # First just get the absorption as a function of energy for incident intensity of 1.
        NormalizedCurve = DoAbsorptionFilter(E, Iin=1, WtPct=WtPct, rho=rho, AbsorptionLength=t[n])
        # NormalizedCurve = CorrectDetectorProperties(E, NormalizedCurve, 50, 50, 0.001, 0.001, 350, 0.001)  # This should improve things,
        # but right now the filter thicknesses are calibrated without it.
        # Multiply that by the flux of the incident beam to get the actual light spectrum hitting the sample through each filter.
        FilteredSpectrum.append(NormalizedCurve * Flux)

    # Show the absorption curves.
    if not quiet:
        plt.figure()
        plt.plot(E, FilteredSpectrum[0], E, FilteredSpectrum[1], E, FilteredSpectrum[2], E, FilteredSpectrum[3])
        plt.legend(['No filter', 'One filter', 'Two filters', 'Three filters'])
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

        # The inner loop convolves the spectrum with its own harmonics to get an apparent spectrum.
        # I.e. how intense the reflection at that energy will be.
        NumHarmonics = 2
        for j, Energy in enumerate(E):
            # Get the index of the 2*E, 3*E, ... harmonics.
            for n in range(NumHarmonics):
                jn = (np.abs(E - (n + 1) * Energy)).argmin()
                ApparentSpectrum[i, j] += k[jn]

                # ApparentSpectrum[i,j] = F(Energy)*k[j] + F(2*Energy)*k[j2] + F(3*Energy)*k[j3]

    # Show the Apparent intensity curves.
    if not quiet:
        plt.figure()
        plt.plot(E, ApparentSpectrum[0, :], E, ApparentSpectrum[1, :], E, ApparentSpectrum[2, :], E,
                 ApparentSpectrum[3, :])

        plt.legend(['No filter', 'One filter', 'Two filters', 'Three filters'])
        plt.title('Absorption curves relative to intensity = 1, with harmonics')

    # At some energy, the ratio of apparent intensities should be the same as the ratios of the measured intensities.
    # That energy will be the right one.  Make new ratio intensities, where each curve is ratioed to the unfiltered curve.
    ApparentRatioSpectrum = ApparentSpectrum.copy()
    for i in range(1, len(t)):
        ApparentRatioSpectrum[i, :] /= ApparentRatioSpectrum[0, :]
    # And don't forget to set the unfiltered spectrum to intensity of 1:
    ApparentRatioSpectrum[0, :] = 1

    # Show the Apparent intensity ratio curves.
    if not quiet:
        plt.figure()
        plt.plot(E, ApparentRatioSpectrum[0, :], E, ApparentRatioSpectrum[1, :], E, ApparentRatioSpectrum[2, :], E,
                 ApparentRatioSpectrum[3, :])
        plt.legend(['No filter', 'One filter', 'Two filters', 'Three filters'])
        plt.title('Absorption curves relative to intensity = 1, with harmonics\nNormalized to the unfiltered spectrum')

    # Now compute the ratio intensities measured.
    Iratio = I.copy().astype('float')
    Iratio[:] /= Iratio[0]
    print Iratio

    # And compare them against the apparent intensity ratio curves.
    RatioComparison = Iratio[:, np.newaxis] - ApparentRatioSpectrum
    FitVal = np.std(RatioComparison, axis=0)
    if not quiet:
        plt.figure()
        plt.plot(E, FitVal)
        print RatioComparison.shape
        plt.plot(E, RatioComparison[0, :])
        plt.plot(E, RatioComparison[1, :])
        plt.plot(E, RatioComparison[2, :])
        plt.plot(E, RatioComparison[3, :])
        plt.title('Fit energy')
        plt.legend(['Best fit curve', 'No Filter', 'One Filter', 'Two filters', 'Three filters'])

    # Print the best fit energy
    print "Best fit energy is %g eV" % E[np.argmin(FitVal)]

    return E[np.argmin(FitVal)]


if __name__ == '__main__':

    # Reflection (-3,3,-3) with energy 8.44862 has intensities:
    # No filter:     108708
    # One filter:    79690.7
    # Two filters:   57407.9
    # Three filters: 37413.6
    # I = np.array([108708, 79690, 57407, 37413]) # Observed energies.
    # I = np.array([ 108708., 79690., 57916., 42499.]) # back computed from jump values.

    # Reflection (-2,4,-2) with energy 12.4727 has intensities:
    # No filter:     175932
    # One filter:    147997
    # Two filters:   116348
    # Three filters: 70706
    # I = np.array([175932, 147997, 116348, 70706]) # Observed energies.
    # I = np.array([179167, 145417, 112917, 87084]) # back computed from jumps.

    # Reflection (-5,5,-3) with energy 15.6641 has intensities:
    # No filter:     71846.3
    # One filter:    63194.4
    # Two filters:   54027.5
    # Three filters: 43934
    # I = np.array([71846, 63194, 54027, 43934]) # Observed energies. #(from ignoring the slopes)
    # I = np.array([71080, 63261, 56302, 50109]) # Observed energies. # using only the discontinuities

    hkls = np.array([[-2, 4, -2],
                     [-3, 3, -1],
                     [-4, 2, -2],
                     [-3, 3, -3],
                     [-5, 3, -1],
                     [-6, 4, -2],
                     [-3, 5, -3],
                     [-6, 6, -4],
                     [-5, 5, -3],
                     [-5, 3, -3],
                     [-4, 6, -6],
                     [-3, 5, -5],
                     [-3, 7, -5],
                     [-7, 5, -3],
                     [-6, 8, -6],
                     [-5, 7, -5],
                     [-8, 6, -6],
                     [-3, 5, -7],
                     [-6, 6, -8],
                     [-9, 5, -3],
                     [-7, 5, -5],
                     [-3, 7, -7],
                     [-5, 7, -7],
                     [-10, 6, -8],
                     [-6, 8, -10],
                     [-9, 5, -5],
                     [-3, 7, -9],
                     [-9, 5, -7],
                     [-5, 7, -9],
                     [-9, 7, -7],
                     [-7, 7, -9],
                     [-11, 5, -7],
                     ])
    TableEperfect = list()
    TableEfit = list()
    TableEError = list()
    TableRelError = list()

    for hkl in hkls:  # np.array([[-5 ,    3 ,   -3]]): #hkls:
        # Now we just compute directly from the hkl.
        (I, Eperfect) = PlotValues(hkl, quiet=True)

        # t = np.array([0, 100, 200, 300]) # Thickness with 0-3 slips each 100 um thick.
        t = np.array([0, 112, 222, 334])  # Thickness with 0-3 slips each 100 um thick.
        rho = 2.2  # g/cm3
        WtPct = np.zeros(pb.MAXELEMENT)
        WtPct[pb.Si - 1] = 46.74
        WtPct[pb.O - 1] = 53.26
        Efit = ComputeSpotEnergy(I, WtPct, rho, t, quiet=True)

        Eerror = np.abs(Efit - Eperfect)
        RelError = np.abs(Efit - Eperfect) / Eperfect * 100
        print "Error in energy is %g.  Relative error is %0.02f percent" % (Eerror, RelError)

        TableEperfect.append(Eperfect)
        TableEfit.append(Efit)
        TableEError.append(Eerror)
        TableRelError.append(RelError)

    # Now these are populated to switch to numpy.
    TableEperfect = np.array(TableEperfect) / 1000  # Convert eV to keV.
    TableEfit = np.array(TableEfit) / 1000
    TableEError = np.array(TableEError)
    TableRelError = np.array(TableRelError)

    # Show a final figure comparing the errors against the flux curve.  Publication quality!
    FluxCurve = np.genfromtxt('../Beamline Characteristics/whitebeamflux.txt', skip_header=1)
    FluxCurve[:, 1] /= max(FluxCurve[:, 1]) / 35
    FluxCurve[:, 0] /= 1000  # Switch to keV from eV.

    fig, ax = QuickPlot.SpecPlot(FluxCurve, boldlevel=3, title='Flux curve compared with errors', xlabel='keV',
                                 ylabel='Points: % relative error\nCurve: flux (arbitrary units)')
    QuickPlot.QuickPlot(TableEperfect, TableRelError, figax=(fig, ax), plottype='scatter', boldlevel=5)
    plt.legend(['Flux Curve', 'Error of best fit values'])

    print ("%% rel error mean = %0.02f and standard deviation: %0.02f" % (np.mean(TableRelError), np.std(TableRelError)))

    print TableEfit
    Keepers = (TableEfit > 11) & (TableEfit < 21)
    print Keepers

    print ("%% rel error mean = %0.02f and standard deviation: %0.02f in region 11-21 keV" % (
        np.mean(TableRelError[Keepers]), np.std(TableRelError[Keepers])))


    def raise_window(figname=None):
        if figname: plt.figure(figname)
        cfm = plt.get_current_fig_manager()
        cfm.window.activateWindow()
        cfm.window.raise_()


    raise_window()
    plt.show()

    # raw_input("Press any key to quit...")
