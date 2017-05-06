# Created 2016, Zack Gainsforth
import matplotlib
#matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import numpy as np
import h5py
import multiprocessing
import time

def LoadScan(HDF5FileName, readwrite=False):
    # Read the HDF file
    if readwrite == False:
        f = h5py.File(HDF5FileName, 'r')  # , swmr=True)
    else:
        f = h5py.File(HDF5FileName, 'r+')#, swmr=True)


    # Make sure this is a version we can read.
    assert f.attrs['MultiLaueVersion'] == '1.0', 'MultiLaue only supports version 1.0 currently.'

    # Get the scan group.
    Scan = f['Scan']
    # Ensure this scan is using a beamline configuration we can process.
    assert Scan.attrs['Synchrotron'] == 'ALS', 'MultiLaue only supports ALS beamline 12.3.2 with the Pilatus detector currently'
    assert Scan.attrs['BeamLine'] == '12.3.2', 'MultiLaue only supports ALS beamline 12.3.2 with the Pilatus detector currently'
    assert Scan.attrs['Detector'] == 'Pilatus', 'MultiLaue only supports ALS beamline 12.3.2 with the Pilatus detector currently'
    # And right now we only do Laue and MultiLaue.
    assert Scan.attrs['ScanType'] in ['Mono', 'Laue', 'MultiLaue'], 'MultiLaue only supports Mono, Laue and MultiLaue scans currently'

    # Done.
    return f, Scan

def MakeSumImageParallelY(RowNumber, NumberOfData, DataQueue, DoneQueue):

    x = []
    for i in range(NumberOfData):
        x.append(DataQueue.get())

    print('Proc %d got %d images' % (RowNumber, len(x)))

    Sum = np.sum(np.array(x), axis=0)

    DoneQueue.put(Sum)
    return

def MakeSumImage(Scan, StatusFunc=None):

    # I originally coded this as single core, and then made a multicore version using multiprocessing.  However, the
    # procedure is IO bound so I am putting it back to single core.  I am leaving the multicore code here because I
    # may need it for the more CPU intensive peak fitting and MultiLaue stuff.

    # MultiStart = time.time()
    #
    # f, Scan = LoadScan('GRA95229_mLaue_6.hdf5')
    # Cube = Scan['DataCube']
    #
    # # Make a sum image with the dimensions of the last two dimensions of the cube (image size)
    # Sum = np.zeros(Cube.shape[2:])
    #
    # jobs = []
    # DoneQueues = []
    #
    # # Now process all the images into it!
    # for y in range(Cube.shape[1]):
    #     print 'Making process %d'%y
    #     DataQueue = multiprocessing.Queue()
    #     DoneQueue = multiprocessing.Queue()
    #     DoneQueues.append(DoneQueue)
    #     for x in range(Cube.shape[0]):
    #         DataQueue.put(Cube[x, y, :, :])
    #     p = multiprocessing.Process(target=MakeSumImageParallelY, args=(y, Cube.shape[0], DataQueue, DoneQueue))
    #     jobs.append(p)
    #     p.start()
    #     #Sum += MakeSumImageParallelY('GRA95229_mLaue_6.hdf5', y)
    #
    # f.close()
    #
    # PartialSums = []
    #
    # for DoneQueue in DoneQueues:
    #     PartialSums.append(DoneQueue.get())
    #
    # Sum = np.sum(np.array(PartialSums), axis=0)
    #
    # print np.max(np.max(Sum))
    #
    # SumLog1 = CleanLog(Sum)
    # #plt.imshow(SumLog, interpolation='none', cmap='gray')
    # #plt.show()
    #
    # MultiTime = time.time() - MultiStart

    #SingleStart = time.time()

    Cube = Scan['DataCube']

    # Make a sum image with the dimensions of the image.
    Sum = np.zeros(Cube.shape[2:4])

    # Now process all the images into it!
    for y in range(Cube.shape[1]):
        for x in range(Cube.shape[0]):
            StatusStr = "Sum image: x=%d, y=%d, Pixel # %d of %d" % (x, y, y * Cube.shape[0] + x + 1, Cube.shape[0] * Cube.shape[1])
            if StatusFunc is not None:
                StatusFunc(StatusStr)
            else:
                print(StatusStr)

            if Scan.attrs['ScanType'] in ['Laue', 'Mono']:
                # The sum image of a Laue scan is the sum of each frame.
                Sum += Cube[x, y, :, :]
            elif Scan.attrs['ScanType'] == 'MultiLaue':
                # MultiLaue sums are just the sum of each frame with the first filter position.
                Sum += Cube[x, y, :, :, 0]

    SumLog = CleanLog(Sum)

    # # plt.imshow(SumLog, interpolation='none', cmap='gray')
    # # plt.show()
    #
    # SingleTime = time.time() - SingleStart
    #
    # print 'Multicore time: %g' % MultiTime
    # print 'Singlecore time: %g' % SingleTime
    # print 'Multicore/SingleCore = %g' % (MultiTime/SingleTime)
    #
    # print 'Numerical Difference: %g' % np.sum(np.sum(SumLog-SumLog1))

    return Sum, SumLog

def MakeStDevImage(Scan, StatusFunc=None):
    """ This produces the standard deviation image and expects the Sum image to be already populated."""

    Cube = Scan['DataCube']
    Sum = Scan['SumImage']

    # Number of pixels in the map.  StDev is computed relative to the mean, i.e. SumImage / N.
    N = Cube.shape[0]*Cube.shape[1]
    MeanImage = Sum[:,:]/N

    StDev = np.zeros(Sum.shape)

    # Now process all the images as the square terms.
    for y in range(Cube.shape[1]):
        for x in range(Cube.shape[0]):
            StatusStr = "StDev image: x=%d, y=%d, Pixel # %d of %d" % (x, y, y * Cube.shape[0] + x + 1, Cube.shape[0] * Cube.shape[1])
            if StatusFunc is not None:
                StatusFunc(StatusStr)
            else:
                print(StatusStr)

            if Scan.attrs['ScanType'] in ['Laue', 'Mono']:
                StDev += (Cube[x, y, :, :] - MeanImage) ** 2
            elif Scan.attrs['ScanType'] == 'MultiLaue':
                # Same as for Laue/mono except we use only the first filter position.
                StDev += (Cube[x, y, :, :, 0] - MeanImage) ** 2


    # N-1 in case of low number of pixels.
    StDev = np.sqrt(StDev / (N-1))
    StDevLog = CleanLog(StDev)

    return StDev, StDevLog

def MakeTopographFromCoordinate(Scan, CoordIn):
    Cube = Scan['DataCube']
    Coord = ConvertCanvasCoordinatesToDataCoordinates(CoordIn)

    Topo = np.zeros(Cube.shape[0:2])

    for y in range(Cube.shape[1]):
        for x in range(Cube.shape[0]):
            if Scan.attrs['ScanType'] in ['Laue', 'Mono']:
                Topo[x,y] += Cube[x, y, Coord[0], Coord[1]]
            elif Scan.attrs['ScanType'] == 'MultiLaue':
                # Same as for Laue/mono except we use only the first filter position.
                Topo[x, y] += Cube[x, y, Coord[0], Coord[1], 0]

    return Topo

def GetSingleImageFromTopographCoordinate(Scan, CoordIn):
    Cube = Scan['DataCube']
    Coord = ConvertCanvasCoordinatesToDataCoordinates(CoordIn)

    if Scan.attrs['ScanType'] in ['Laue', 'Mono']:
        SingleImage = Cube[Coord[0], Coord[1], :, :]
        EnergyImage = None
        EnergyFitImage = None
    elif Scan.attrs['ScanType'] == 'MultiLaue':
        SingleImage = Cube[Coord[0], Coord[1], :, :, 0]
        EnergyImage = Scan['EnergyCube'][Coord[0], Coord[1], :, :]
        EnergyFitImage = Scan['EnergyFitValCube'][Coord[0], Coord[1], :, :]

    return SingleImage, EnergyImage, EnergyFitImage

def ConvertCanvasCoordinatesToDataCoordinates(CanvasCoordinate):
    c = np.array(CanvasCoordinate)
    # The data is stored as mxn instead of x,y so transpose the coordinates.
    # The canvas reports each value at the center of the pixels instead of the corner, so we also add an offset of 1/2.
    c[0] = np.floor(CanvasCoordinate[1] + 0.5)
    c[1] = np.floor(CanvasCoordinate[0] + 0.5)
    return c

def CleanLog(Val):
    # Returns a log of an image, but without infinities or nans.
    LogVal = np.log(Val)
    LogVal[np.isinf(LogVal)] = 0
    LogVal = np.nan_to_num(LogVal)
    return LogVal

if __name__ == '__main__':

    f, Scan = LoadScan('GRA95229_mLaue_7.hdf5', readwrite=True)
    Sum, SumLog = MakeSumImage(Scan)
    Scan.create_dataset('SumImage', data=Sum)
    # Scan.create_dataset('SumImage', data=Sum)
    StDev, StDevLog = MakeStDevImage(Scan)

    f.close()

