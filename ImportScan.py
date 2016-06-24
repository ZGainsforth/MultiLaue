# Created 2016, Zack Gainsforth
import numpy as np
import h5py
import os
import sys
import skimage.external.tifffile as tifffile
import json
import BasicProcessing

def WriteExampleConfigFile():
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

    # First we just need the info about the raw data.
    RawScanInfo = Config['RawScanInfo']

    # Make the HDF file
    f = h5py.File(Config['ScanInfo']['ScanName'] + '.hdf5', 'w')
    # Version number goes on the root node.
    f.attrs['MultiLaueVersion'] = Config['MultiLaueVersion']['Version']

    # All the data goes in the group "scan".
    Scan = f.create_group('Scan')
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

    f.close()

if __name__ == '__main__':

    # Just an example to get started.
    WriteExampleConfigFile()

    # Read the scan into an HDF5 file.
    ImportScan('LaueScan.json')