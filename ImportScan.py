# Created 2016, Zack Gainsforth
import numpy as np
import h5py
import os
import sys
import skimage.external.tifffile as tifffile
import json
import BasicProcessing
import PhysicsBasics as pb

def WriteExampleMultiLaueConfigFile():
    """Importing data into MultiLaue requires knowing all the beamline parameters and such.  These can be written into
    a text file (json format).  This function just writes an example config file -- you probably want to make your
    future files by hand with the data custom to the scan."""

    MultiLaueVersion = {'Version': 1.0}

    ScanInfo = {'ScanName': 'GRA95229_mLaue_7', 'ScanDate': '2016-04-28', 'xPixels': 8, 'yPixels': 7, 'zPixels': 4,
                'ScanType': 'MultiLaue', 'Energy': -1, 'Synchrotron': 'ALS', 'BeamLine': '12.3.2', 'Detector': 'Pilatus'}

    RawScanInfo = {'RawDataPath': '/Users/Zack/Desktop/20160428 - 12.3.2/003 GRA95229,30/011 GRA95229_mLaue_7',
                   'LineDirectoryFormat': 'GRA95229_mLaue7_%02d', 'FileNameFormat': 'GRA95229_mLaue7_%02d_%05d.tif'}

    Calibration = {'DetName': 'ALS12.3.2Pilatus', 'Energy': -1, 'xmm': 179.0, 'TwoThetaCenter': 75.0, 'xPixels': 1043,
                   'xCenter': 538.153, 'yPixels': 981, 'DetectorDistance': 162.498, 'yCenter': 230.63, 'ymm': 168.387,
                   'yaw': 0, 'pitch': 0, 'roll': 0}

    # Make the WtPcts array for the filters.  They are all the same in this case.
    WtPct = [0.0]*pb.MAXELEMENT
    WtPct[pb.Si - 1] = 46.74
    WtPct[pb.O - 1] = 53.26

    FilterInfo = {'NumberOfPositions': 4,
                  'FilterThicknesses': [0, 112, 222, 334], # Microns
                  'FilterDensity': 2.2, # g/cc
                  'FilterWtPcts': [WtPct, WtPct, WtPct, WtPct]
                  }

    Config = {'MultiLaueVersion': MultiLaueVersion, 'ScanInfo': ScanInfo, 'RawScanInfo': RawScanInfo, 'Calibration': Calibration, 'FilterInfo': FilterInfo}

    ConfigStr = json.dumps(Config, indent=4)

    with open('MultiLaueScan.json', 'w') as f:
        f.write(ConfigStr)

def WriteExampleLaueConfigFile():
    """Importing data into MultiLaue requires knowing all the beamline parameters and such.  These can be written into
    a text file (json format).  This function just writes an example config file -- you probably want to make your
    future files by hand with the data custom to the scan."""

    MultiLaueVersion = {'Version': 1.0}

    ScanInfo = {'ScanName': 'GRA95229_mLaue_6', 'ScanDate': '2016-04-28', 'xPixels': 26, 'yPixels': 24, 'zPixels': 1,
                'ScanType': 'Laue', 'Energy': -1, 'Synchrotron': 'ALS', 'BeamLine': '12.3.2', 'Detector': 'Pilatus'}

    RawScanInfo = {'RawDataPath': '/Users/Zack/Desktop/20160428 - 12.3.2/003 GRA95229,30/010 GRA95229_Laue_6',
                   'FileNameFormat': 'GRA95229_mLaue_6_%05d.tif', 'StartIndex': 1, 'EndIndex': 624}

    Calibration = {'DetName': 'ALS12.3.2Pilatus', 'Energy': -1, 'xmm': 179.0, 'TwoThetaCenter': 75.0, 'xPixels': 1043,
                   'xCenter': 538.153, 'yPixels': 981, 'DetectorDistance': 162.498, 'yCenter': 230.63, 'ymm': 168.387,
                   'yaw': 0, 'pitch': 0, 'roll': 0}

    Config = {'MultiLaueVersion': MultiLaueVersion, 'ScanInfo': ScanInfo, 'RawScanInfo': RawScanInfo, 'Calibration': Calibration}

    ConfigStr = json.dumps(Config, indent=4)

    with open('LaueScan.json', 'w') as f:
        f.write(ConfigStr)

def ReadConfigFile(FileName):
    """Read config file with scan info etc."""
    with open(FileName, 'r') as f:
        ConfigStr = f.read()

    Config = json.loads(ConfigStr)

    # Do basic sanity checks.
    assert Config['MultiLaueVersion']['Version'] == 1.0, 'MultiLaue only supports version 1.0 currently.'
    assert Config['ScanInfo']['Synchrotron'] == 'ALS', 'MultiLaue only supports ALS beamline 12.3.2 with the Pilatus detector currently'
    assert Config['ScanInfo']['BeamLine'] == '12.3.2', 'MultiLaue only supports ALS beamline 12.3.2 with the Pilatus detector currently'
    assert Config['ScanInfo']['Detector'] == 'Pilatus', 'MultiLaue only supports ALS beamline 12.3.2 with the Pilatus detector currently'

    return Config

def ImportScan(ConfigFile):
    # Read in the info about the scan so we can import the data into HDF5.
    Config = ReadConfigFile(ConfigFile)

    # Check what kind of scan this is.
    if Config['ScanInfo']['ScanType'] == 'Laue':
        return ImportLaueScan(Config)
    elif Config['ScanInfo']['ScanType'] == 'MultiLaue':
        return ImportMultiLaueScan(Config)
    else:
        print Config['ScanInfo']['ScanType'] + ' is an unsupported scan type.'

def ImportLaueScan(Config):
    # First we just need the info about the raw data.
    RawScanInfo = Config['RawScanInfo']

    # Make the HDF file
    h5 = h5py.File(Config['ScanInfo']['ScanName'] + '.hdf5', 'w')
    # Version number goes on the root node.
    h5.attrs['MultiLaueVersion'] = '1.0'

    # All the data goes in the group "scan".
    Scan = h5.create_group('Scan')
    # The ScanInfo section of the config file is the attributes for the scan.
    for k,v in Config['ScanInfo'].items():
        Scan.attrs[k] = v

    # Add a calibration group.
    Calibration = Scan.create_group('Calibration')
    # The Calibration section of the config file is the attributes for the calibration.
    for k,v in Config['Calibration'].items():
        Calibration.attrs[k] = v

    # Now make the data cube.  For Laue this is 4D: x,y stage, and x,y image.
    CubeShape = (Config['ScanInfo']['xPixels'], Config['ScanInfo']['yPixels'], Config['Calibration']['xPixels'],
             Config['Calibration']['yPixels'])
    # Note compression greatly speeds up the later processing since these stacks are mostly IO bound.  (Factor of 4 compression is a 4X performance gain!)
    Cube = Scan.create_dataset('DataCube', shape=CubeShape, dtype='float32', chunks=(1,1,200,200), compression='gzip')

    # We also have a grid for the metadata stored in each tiff file.
    dt = h5py.special_dtype(vlen=bytes)
    MetadataCube = Scan.create_dataset('MetadataCube', shape=CubeShape[:2], dtype=dt)

    # Now loop through all the images and stuff them in the data cube.
    FilePath = Config['RawScanInfo']['RawDataPath']
    FileNameFormat = Config['RawScanInfo']['FileNameFormat']

    # For each pixel in the stage scan (x,y stage) we will insert a 2D image.
    for y in range(Cube.shape[1]):
        for x in range(Cube.shape[0]):

            # The images are recorded by the beamline as a linear sequence.  Get our index into that sequence.
            i = y*Cube.shape[0] + x + Config['RawScanInfo']['StartIndex']
            # If the scan was aborted early, then we won't have enough images to fill the cube.
            if i > Config['RawScanInfo']['EndIndex']:
                print 'Number of images does not completely fill the data cube.  Substituting zeros for remainder of cube.'
                break

            # Read this image in and populate the cube.
            try:
                with tifffile.TiffFile(os.path.join(FilePath, FileNameFormat % i)) as T:
                    #print T[0].tags['image_description'].value
                    print "Loading image: x=%d, y=%d, Pixel # %d of %d" % (x, y, y * Cube.shape[0] + x + 1, Cube.shape[0] * Cube.shape[1])
                    Cube[x, y, :, :] = T[0].asarray()
                    MetadataCube[x,y] = T[0].tags['image_description'].value
            except IOError:
                print FileNameFormat % i + ' could not be found.  Substituting zeros.'

    # Now make the sum image (and log of the sum image) from the Cube.
    Sum, SumLog = BasicProcessing.MakeSumImage(Scan)
    Scan.create_dataset('SumImage', data=Sum)
    Scan.create_dataset('SumLogImage', data=SumLog)

    # And a stdev image.
    StDev, StDevLog = BasicProcessing.MakeStDevImage(Scan)
    Scan.create_dataset('StDevImage', data=StDev)
    Scan.create_dataset('StDevLogImage', data=StDevLog)

    h5.close()


def ImportMultiLaueScan(Config):
    # Make the HDF file
    h5 = h5py.File(Config['ScanInfo']['ScanName'] + '.hdf5', 'w')
    # Version number goes on the root node.
    h5.attrs['MultiLaueVersion'] = '1.0'

    # All the data goes in the group "scan".
    Scan = h5.create_group('Scan')
    # The ScanInfo section of the config file is the attributes for the scan.
    for k,v in Config['ScanInfo'].items():
        Scan.attrs[k] = v

    # Add a calibration group.
    Calibration = Scan.create_group('Calibration')
    # The Calibration section of the config file is the attributes for the calibration.
    for k,v in Config['Calibration'].items():
        Calibration.attrs[k] = v

    # Now make the data cube.  For MultiLaue this is 5D: x,y stage,  x,y image by # filters.
    CubeShape = (Config['ScanInfo']['xPixels'], Config['ScanInfo']['yPixels'], Config['Calibration']['xPixels'],
             Config['Calibration']['yPixels'], Config['FilterInfo']['NumberOfPositions'])
    # Note compression greatly speeds up the later processing since these stacks are mostly IO bound.  (Factor of 4 compression is a 4X performance gain!)
    Cube = Scan.create_dataset('DataCube', shape=CubeShape, dtype='float32', chunks=(1,1,200,200,4), compression='gzip')#, compression_opts=7) # Compression 7 will improve by 10% but take waaay longer for the first import.

    # We also have a grid for the metadata stored in each tiff file.
    # The metadata has stage pixels, and filter pixels, so 3D.
    dt = h5py.special_dtype(vlen=bytes)
    MetadataCube = Scan.create_dataset('MetadataCube', shape=np.array(CubeShape)[[0,1,-1]], dtype=dt)

    # Now loop through all the images and stuff them in the data cube.
    FilePath = Config['RawScanInfo']['RawDataPath']
    LineDirectoryFormat = Config['RawScanInfo']['LineDirectoryFormat']
    FileNameFormat = Config['RawScanInfo']['FileNameFormat']
    FilterPositions = Config['FilterInfo']['NumberOfPositions']

    # Compute how many images total.
    NumImages = np.array(Cube.shape)[[0,1,-1]].prod()
    n = 1 # Starting with the first image.

    # For each pixel in the stage scan (x,y stage) we will insert a 2D image.
    for y in range(Cube.shape[1]):
        for x in range(Cube.shape[0]):
            for f in range(Cube.shape[-1]):

                # Read this image in and populate the cube.
                # Each line of the scan is stored in a subdir with the name LineDirectoryFormat.
                # Compute the index of this image.  It is the x coordinate x the filter (x1,f1, x1,f2, x2,f1, x2,f2, x3,f1 ...)
                i = x*FilterPositions + f

                FullPath = os.path.join(FilePath, LineDirectoryFormat%(y+1), FileNameFormat % (y+1, i+1))
                try:
                    with tifffile.TiffFile(FullPath) as T:
                        print "Loading image: x=%d, y=%d, f=%d, Frame # %d of %d" % (x, y, f, n, NumImages)
                        Cube[x, y, :, :, f] = T[0].asarray()
                        MetadataCube[x, y, f] = T[0].tags['image_description'].value
                except IOError:
                    print FileNameFormat % (y+1,i+1) + ' could not be found.  Substituting zeros.'

                # Increment the frame count.
                n += 1

    # # Now make the sum image (and log of the sum image) from the Cube.
    # Sum, SumLog = BasicProcessing.MakeSumImage(Scan)
    # Scan.create_dataset('SumImage', data=Sum)
    # Scan.create_dataset('SumLogImage', data=SumLog)
    #
    # # And a stdev image.
    # StDev, StDevLog = BasicProcessing.MakeStDevImage(Scan)
    # Scan.create_dataset('StDevImage', data=StDev)
    # Scan.create_dataset('StDevLogImage', data=StDevLog)

    h5.close()

if __name__ == '__main__':

    # # Just an example to get started.
    # WriteExampleConfigFile()
    # # Read the scan into an HDF5 file.
    # ImportScan('LaueScan.json')

    # Just an example to get started.
    #WriteExampleMultiLaueConfigFile()
    # Read the scan into an HDF5 file.
    ImportScan('MultiLaueScan.json')
