# Created 2016, Zack Gainsforth
import matplotlib
#matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import numpy as np
import h5py
import multiprocessing
import time

def LoadScan(HDF5FileName):
    # Read the HDF file
    f = h5py.File(HDF5FileName, 'r')#, swmr=True)

    # Make sure this is a version we can read.
    assert f.attrs['MultiLaueVersion'] == 1.0, 'MultiLaue only supports version 1.0 currently.'

    # Get the scan group.
    Scan = f['Scan']
    # Ensure this scan is using a beamline configuration we can process.
    assert Scan.attrs['Synchrotron'] == 'ALS', 'MultiLaue only supports ALS beamline 12.3.2 with the Pilatus detector currently'
    assert Scan.attrs['BeamLine'] == '12.3.2', 'MultiLaue only supports ALS beamline 12.3.2 with the Pilatus detector currently'
    assert Scan.attrs['Detector'] == 'Pilatus', 'MultiLaue only supports ALS beamline 12.3.2 with the Pilatus detector currently'
    # And right now we only do Laue.
    assert Scan.attrs['ScanType'] == 'Laue', 'MultiLaue only supports Laue scans currently'

    # Done.
    return f, Scan

def MakeSumImageParallelY(RowNumber, NumberOfData, DataQueue, DoneQueue):

    x = []
    for i in range(NumberOfData):
        x.append(DataQueue.get())

    print 'Proc %d got %d images' % (RowNumber, len(x))

    Sum = np.sum(np.array(x), axis=0)

    DoneQueue.put(Sum)
    return

def MakeSumImage(Scan):

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
    # SumLog1 = np.log(Sum)
    # #plt.imshow(SumLog, interpolation='none', cmap='gray')
    # #plt.show()
    #
    # MultiTime = time.time() - MultiStart


    SingleStart = time.time()

    Cube = Scan['DataCube']

    # Make a sum image with the dimensions of the last two dimensions of the cube (image size)
    Sum = np.zeros(Cube.shape[2:])

    # Now process all the images into it!
    for y in range(Cube.shape[1]):
        for x in range(Cube.shape[0]):
            print "Sum image: x=%d, y=%d, Pixel # %d of %d" % (x, y, y * Cube.shape[0] + x + 1, Cube.shape[0] * Cube.shape[1])
            Sum += Cube[x, y, :, :]

    SumLog = np.log(Sum)


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

def MakeStDevImage(Scan):
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
            print "StDev image: x=%d, y=%d, Pixel # %d of %d" % (x, y, y * Cube.shape[0] + x + 1, Cube.shape[0] * Cube.shape[1])
            StDev += (Cube[x, y, :, :] - MeanImage)**2

    # N-1 in case of low number of pixels.
    StDev = np.sqrt(StDev) / (N-1)
    StDevLog = np.log(StDev)

    return StDev, StDevLog

if __name__ == '__main__':

    f, Scan = LoadScan('GRA95229_mLaue_6.hdf5')
    Sum, SumLog = MakeSumImage(Scan)
    # Scan.create_dataset('SumImage', data=Sum)
    StDev, StDevLog = MakeStDevImage(Scan)

    f.close()
