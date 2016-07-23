# Created 2016, Zack Gainsforth
#import matplotlib
#matplotlib.use('Qt4Agg')
#import matplotlib.pyplot as plt
import numpy as np

# This will be changed with the QT version shortly.
#import QuickWxDialogs as Dlgs

class DetectorGeometry():
    # This class contains all the information about an XRD stack.
    DirectoryName = None
    FileNameFormat = None
    shape = (1,1)
    Calibration = {'xmm': 179.0, 'TwoThetaCenter': 75.0, 'xPixels': 1043, 'xCenter': 538.153, 'yPixels': 981,
         'DetectorDistance': 162.498, 'yCenter': 230.63, 'ymm': 168.387, 'DetName': 'ALS12.3.2Pilatus'}

    def __init__(self, shape=(1, 1), Calibration=None):
        """
        :param shape: How many pixels in the stack.  Can be 2D (Laue/Mono) or 3D (MultiLaue)

        >>> C = dict()
        >>> C['DetName'] = 'ALS12.3.2Pilatus'
        >>> C['DetectorDistance'] = 162.498
        >>> C['TwoThetaCenter'] = 75.000
        >>> C['xPixels'] = 1043
        >>> C['yPixels'] = 981
        >>> C['xCenter'] = 538.153
        >>> C['yCenter'] = 230.630
        >>> C['xmm'] = 719.000
        >>> C['ymm'] = 168.387
        >>> S = DetectorGeometry(shape=(1,1), Calibration=C)

        """
        self.shape = shape

        if Calibration is not None:
            self.SetCalibration(Calibration)

    def SetCalibration(self, Calibration):
        """

        :param Calibration: Dictionary with the calibration parameters for the detector.
        :return: None.
        """

        # Calibration is a dictionary which has all the needed fields.
        assert(Calibration['DetName']=='ALS12.3.2Pilatus'), "For now, we only support the Pilatus detector on ALS Beamline 12.3.2."
        assert(Calibration['DetectorDistance'] > 0), 'The sample to detector distance must be positive.'
        assert(0 <= Calibration['TwoThetaCenter'] <= 90), 'The coordinate of the center pixel must be between 0 and 90 degrees since the detector moves between 0 and 90 degrees.'
        assert (Calibration['xPixels'] > 0), 'The number of pixels wide (+x, -Chi direction) and tall (-y, or +TwoTheta direction) must be > 0'
        assert (Calibration['yPixels'] > 0), 'The number of pixels wide (+x, -Chi direction) and tall (-y, or +TwoTheta direction) must be > 0'
        assert (0 <= Calibration['xCenter'] <= Calibration['xPixels']), 'The center pixel (where TwoTheta = TwoThetaCenter) must be inside the detector!'
        assert (0 <= Calibration['yCenter'] <= Calibration['yPixels']), 'The center pixel (where TwoTheta = TwoThetaCenter) must be inside the detector!'
        assert (Calibration['xmm'] > 0), 'The detector must be more than 0 mm wide (+x, -Chi direction)'
        assert (Calibration['ymm'] > 0), 'The detector must be more than 0 mm tall (-y, +TwoTheta direction)'

        # It passed all the assertions so save the calibration.
        self.Calibration = Calibration

    def GetTwoThetaChi(self, x, y):
        """
        Convert x,y to TwoTheta and Chi
        :param x:
        :param y:
        :return:

        >>> C = dict()
        >>> C['DetName'] = 'ALS12.3.2Pilatus'
        >>> C['DetectorDistance'] = 162.498
        >>> C['TwoThetaCenter'] = 75.000
        >>> C['xPixels'] = 1043
        >>> C['yPixels'] = 981
        >>> C['xCenter'] = 538.153
        >>> C['yCenter'] = 230.630
        >>> C['xmm'] = 179.000
        >>> C['ymm'] = 168.387
        >>> S = DetectorGeometry(shape=(1,1), Calibration=C)
        >>> print S.GetTwoThetaChi(538.153,230.630) # Center pixel
        (75.0, 0.0)
        >>> print S.GetTwoThetaChi(538,1) # Some other spots
        (88.634370664189291, 0.0090000280495111974)
        >>> print S.GetTwoThetaChi(538.153,270)
        (72.618616173180811, 0.0)
        >>> print S.GetTwoThetaChi(911,371)
        (68.249050477686907, -23.002955166333052)
        >>> print S.GetTwoThetaChi(97,717)
        (51.651056635904851, 29.220718216276616)
        """

        C = self.Calibration

        assert (C['DetName'] == 'ALS12.3.2Pilatus'), "For now, we only support the Pilatus detector on ALS Beamline 12.3.2."

        # TwoTheta = np.degrees(np.arccos(np.cos(np.radians(C['TwoThetaCenter'])) + C['ymm'] * (y - C['yCenter']) * np.sin(np.radians(C['TwoThetaCenter'])) / C['yPixels'] / C['DetectorDistance']))
        # Chi = np.degrees(np.arcsin(-C['xmm'] * (x - C['xCenter']) / C['xPixels'] / C['DetectorDistance'] / np.sin(np.radians(TwoTheta))))
        # print "x = %g; y = %g" % (x, y)
        # print "C = " + repr(C)
        # print "TwoTheta = np.degrees(np.arccos(np.cos(np.radians(C['TwoThetaCenter'])) + C['ymm'] * (y - C['yCenter']) * np.sin(np.radians(C['TwoThetaCenter'])) / C['yPixels'] / C['DetectorDistance']))"

        # kin is the vector of the incoming X-ray beam.  It is down the z-axis.
        kin = np.array([0, 0, 1])

        # Two theta of the center of the detector
        TwoThetaCenter = np.radians(C['TwoThetaCenter'])

        #Vector to the center of the detector.
        kdet = np.array([0, # Note the detector is assumed never to wander laterally, but always to stay centered in the yz plane.
                         C['DetectorDistance'] * np.sin(TwoThetaCenter),
                         C['DetectorDistance'] * np.cos(TwoThetaCenter)])

        # Based on the detector tilt, and the x,y coordinate we are after, get the vector which goes from the center pixel
        # to the pixel of interest.
        dl = (y-C['yCenter']) * (C['ymm']/C['yPixels'])
        dx = - (x-C['xCenter']) * (C['xmm']/C['xPixels']) # Since the detector is flat in the x direction, the component is easy.
        dy = - dl * np.cos(TwoThetaCenter)
        dz = dl * np.sin(TwoThetaCenter)
        dk = np.array([dx, dy, dz])

        # TODO: IMPLEMENT YAW PITCH ROLL.
        # The basis attached to the detector is defined by z = normal to plane of detector, x,y = in the plane of the detector.
        # Center of detector is therefore at xcent,ycent,0. yaw, pitch and roll are defined as rotation around z,x and y respectively.
        # The rotation convention used is Xyz: first rotate around x (pitch) then y (roll) then z (yaw). -- NT

        # Make a vector from the sample to the pixel of interest.
        k = kdet + dk
        kmag = np.sqrt(np.dot(k,k))

        # And finally TwoTheta comes as the dot product of kin (incident beam) and k (diffracted beam).
        TwoTheta = np.degrees(np.arccos(np.dot(kin, k)/kmag))

        # Chi is the rotation in the xy plane of the diffracted beam.
        kchi = k
        kchi[2] = 0 # Lose the z coordinate.
        kchimag = np.sqrt(np.dot(kchi,kchi))
        # Chi comes from the dot product, but is the angle between kchi and the y-axis.  Hence arcsin, not arccos.
        Chi = np.degrees(np.arcsin(np.dot(kchi, np.array([1,0,0]))/kchimag))

        return (TwoTheta, Chi, kmag)

if __name__ == '__main__':
    import doctest
    doctest.testmod()