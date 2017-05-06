import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import PhysicsBasics as pb
from skimage.feature import blob_log
from skimage.io import imread
from multiprocessing import Pool
from matplotlib.patches import Circle
from scipy.stats import mode
from tabulate import tabulate
import re
from io import BytesIO
import pandas as pd


def LocatePeaksInXRD(Image, Beamline='12.3.2', Detector='Pilatus', Quiet=True, Threshold=None):
    ''' Given an XRD image, find the peaks in it and return a list of peak coordinates.  Threshold is for the blob_log methoc.'''
    assert (Beamline == '12.3.2') and (Detector=='Pilatus'), 'Only the Pilatus detector on the 12.3.2 beamline is supported.'
    assert (Image.shape == (981,1043)), 'This does not appear to be an image from the Pilatus detector on beamline 12.3.2.' # This is the image shape for the pilatus images on 12.3.2

    # The Blob Laplacian of Gaussian (blob_log) algorithm wants normalized data.  We also need to take the log for XRD data since the peaks are orders of magnitude brighter than the background.
    LogNormImage = np.nan_to_num(np.log(Image.copy()))
    LogNormImage[LogNormImage < 0] = 0
    LogNormImage /= np.max(LogNormImage)

    if Threshold is not None:
        peaks = DoOneBlobLog1232Pilates(LogNormImage, Threshold)
    else:
        # User wants to autoselect the threshold.  We do this by trying a bunch of threshholds and choosing the elbow of the curve.
        # There is not a good way to guess this yet.  For now, use a default value.
        peaks = DoOneBlobLog1232Pilates(LogNormImage, Threshold=0.1)
        #TODO Make a threshold guesser with ML or some such in the future.

    # If the user wants to see what is up, then we will draw him a plot.`
    if Quiet == False:
        ax = plt.subplot(111)
        ax.imshow(LogNormImage)
        plt.title('Log scale, %d peaks, Threshold=%0.2g'%(len(peaks), Threshold))
        for p in peaks:
            ax.text(p[1], p[0], '/')

    return peaks, Threshold

def DoOneBlobLog1232Pilates(LogNormImage, Threshold=0.07):
    ''' In the future we may support multiple detectors and beamlines.  In such case, we will want to do the peak finding in a fashion that suits each detector.
    This is the routine for ALS Beamline 12.3.2, Pilatus detector.'''

    # Locate all the diffraction peaks.
    blobs = blob_log(LogNormImage, threshold=Threshold, max_sigma=3)

    # The Pilatus detector on 12.3.2 has a 4 vertical and one horizontal stripe down the middle which are the locations that the detector segments join.
    # The blob function finds the corners of the detector segments which is incorrect.  So we'll exclude any peaks within a certain x or y distance of the corners.
    peaks = []
    for b in blobs:
        # exclude anything within 15 pixels of the horizontal line down the middle.
        if abs(b[0] - 490) < 15:
            continue
        # exclude anything within 25 pixels of any of the 4 fat vertical lines.
        d = abs(b[1] % (1043 / 5))
        if (d > ((1043 / 5) - 25)) or (d < 25):
            continue
        # It's a good peak, save it.
        peaks.append(b)

    return peaks

def GetPeakIntensities(Image, Peaks):
    ''' The peaks have been labeled and are in the array Peaks.shape = (n,3).  Each row is [x, y, peak width].  The simplest method for integrating the peak is to look at
    the noise level (mode of the pixels in the area around the peak) and subtract that floor off as a constant value.  Then integrate the '''

    LocalRange = 10 # Select some pixels around the peak in order to encompass the peak and some background.

    # We will make a new column to store the intensities of each peak.
    Intensities = []
    for p in Peaks:
        xpixel = p[0].astype(int)
        ypixel = p[1].astype(int)

        # avoid peaks at the boundaries.
        if (xpixel - LocalRange < 0) or (xpixel + LocalRange+1 > Image.shape[0]) or (ypixel - LocalRange < 0) or (ypixel + LocalRange+1 > Image.shape[1]):
            Intensities.append(np.nan)
            continue

        # Now choose a box around the peak.
        ImLocal = Image[xpixel-LocalRange:xpixel+LocalRange+1, ypixel-LocalRange:ypixel+LocalRange+1].copy()

        # Remove the background which is considered to be a constant equal to the mode of the image.
        BkgLevel = mode(ImLocal, axis=None)[0]
        ImLocal -= BkgLevel

        # Make a mask to include only peaks which are more than 3x the background.
        ImMask = ImLocal.copy()
        ImMask[ImMask < 3 * BkgLevel] = 0
        ImMask[ImMask >= 3 * BkgLevel] = 1

        # Now mask the main image and integrate.
        ImMask *= ImLocal
        Intensities.append(np.sum(ImMask))

    Peaks = np.hstack((Peaks, np.array(Intensities)[:,np.newaxis]))

    return Peaks

def Read1232IndFile(FileName=None):
    # ALS beamline 12.3.2 using the XMAS software which will return an ind file containing the intensity of each peak found after indexing a crystal.  Also has hkl, two theta, etc.  This can be used
    # for training our algorithms.
    # Load the ind file
    with open(FileName, 'r') as f:
        WholeFile = f.read()

    # Pull out the chunk of the file that contains the indexation table (starts with number of indexed reflections and ends with the deviatoric stuff.
    s = re.search('(number of indexed reflections:\s*[0-9]*[\r\n]*)([a-zA-Z0-9\s\(\)_\.-]*)( dev1, dev2)', WholeFile)
    ReflStr = s.group(2)

    # Nobu has a typo in his files, so two columns are accidentally blended together.  Fix it.
    ReflStr = ReflStr.replace('chi(deg)intensity', 'chi(deg) intensity')

    # Now turn the text into a named numpy array.
    ReflStr = BytesIO(ReflStr.encode('utf-8'))
    R = np.genfromtxt(ReflStr, names=True)

    # Sort by hkl
    R.sort(order=('h', 'k', 'l'))

    # print(tabulate(R, headers=R.dtype.names))
    Rpd = pd.DataFrame(R)

    Rpd.to_csv(FileName + '.csv')

    #Rpd.head()
    return Rpd


if __name__ == '__main__':
    #im = imread('albite_test_009.tif')

    # im = imread('/Users/Zack/Desktop/20160929_12.3.2/006-Albite/albite_1_ml/albite_1_ml_00001.tif')
    # peaks, _ = LocatePeaksInXRD(im.T, Quiet=False, Threshold=0.06)
    # peaks = GetPeakIntensities(im.T, peaks)
    # im2 = imread('/Users/Zack/Desktop/20160929_12.3.2/006-Albite/albite_1_ml/albite_1_ml_00002.tif')
    # peaks2 = GetPeakIntensities(im2.T, peaks)
    # im3 = imread('/Users/Zack/Desktop/20160929_12.3.2/006-Albite/albite_1_ml/albite_1_ml_00003.tif')
    # peaks3 = GetPeakIntensities(im3.T, peaks)

    ImageList = ['', '', '']
    ImageList = ['/Users/Zack/Desktop/20160929_12.3.2/006-Albite/albite_1_ml/albite_1_ml_00001.tif', '/Users/Zack/Desktop/20160929_12.3.2/006-Albite/albite_1_ml/albite_1_ml_00002.tif', '/Users/Zack/Desktop/20160929_12.3.2/006-Albite/albite_1_ml/albite_1_ml_00003.tif']
    ImageList = ['/Users/Zack/Desktop/20160929_12.3.2/007-TiO2/TiO2_1_ml/TiO2_1_ml_00001.tif', '/Users/Zack/Desktop/20160929_12.3.2/007-TiO2/TiO2_1_ml/TiO2_1_ml_00002.tif', '/Users/Zack/Desktop/20160929_12.3.2/007-TiO2/TiO2_1_ml/TiO2_1_ml_00003.tif']
    ImageList = ['/Users/Zack/Desktop/20160929_12.3.2/002-Magnetite/magnetite_1/magnetite_1_00001.tif', '/Users/Zack/Desktop/20160929_12.3.2/002-Magnetite/magnetite_1/magnetite_1_00002.tif', '/Users/Zack/Desktop/20160929_12.3.2/002-Magnetite/magnetite_1/magnetite_1_00003.tif']
    ImageList = ['/Users/Zack/Desktop/20160929_12.3.2/003-Diopside/diopside_ml_1/diopside_ml_1_00001.tif', '/Users/Zack/Desktop/20160929_12.3.2/003-Diopside/diopside_ml_1/diopside_ml_1_00002.tif', '/Users/Zack/Desktop/20160929_12.3.2/003-Diopside/diopside_ml_1/diopside_ml_1_00003.tif']
    ImageList = ['/Users/Zack/Desktop/20160929_12.3.2/008-Quartz/quartz_c_ml/quartz_c_ml_00001.tif', '/Users/Zack/Desktop/20160929_12.3.2/008-Quartz/quartz_c_ml/quartz_c_ml_00002.tif', '/Users/Zack/Desktop/20160929_12.3.2/008-Quartz/quartz_c_ml/quartz_c_ml_00003.tif']
    ImageList = ['/Users/Zack/Desktop/20160929_12.3.2/008-Quartz/quartz_flat_ml/quartz_flat_ml_00001.tif', '/Users/Zack/Desktop/20160929_12.3.2/008-Quartz/quartz_flat_ml/quartz_flat_ml_00002.tif', '/Users/Zack/Desktop/20160929_12.3.2/008-Quartz/quartz_flat_ml/quartz_flat_ml_00003.tif']
    ImageList = ['/Users/Zack/Desktop/20160929_12.3.2/008-Quartz/quartz_sharp_ml/quartz_sharp_ml_00001.tif', '/Users/Zack/Desktop/20160929_12.3.2/008-Quartz/quartz_sharp_ml/quartz_sharp_ml_00002.tif', '/Users/Zack/Desktop/20160929_12.3.2/008-Quartz/quartz_sharp_ml/quartz_sharp_ml_00003.tif']

    im = imread(ImageList[0])
    peaks, _ = LocatePeaksInXRD(im.T, Quiet=False, Threshold=0.06)
    peaks = GetPeakIntensities(im.T, peaks)
    im2 = imread(ImageList[1])
    peaks2 = GetPeakIntensities(im2.T, peaks)
    im3 = imread(ImageList[2])
    peaks3 = GetPeakIntensities(im3.T, peaks)

    #peaks = np.array(peaks)
    peaks[:,1] = im.shape[0] - peaks[:,1]

    print(peaks.shape)
    peaks = np.hstack((peaks, peaks2[:,-1,np.newaxis], peaks3[:,-1,np.newaxis]))
    print(peaks.shape)

    print(tabulate(peaks, headers=['x', 'y', 'width', 'nofilter', 'onefilter', 'twofilters']))
    print('Number of peaks: ', peaks.shape[0])
    #Ind = Read1232IndFile(FileName='albite_test_009.IND')
    #Ind.head()
    plt.show()
