# Created 2016, Zack Gainsforth
from __future__ import division
# import matplotlib
# #matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import numpy as np
import re
import StringIO
import json
import pickle

# How many files are in the sequence as we move the filter arm.
NumFiles = 150

Rarray = dict()

def PlotValues(hkl, quiet=False):

    # Intensity, energy of a given reflection as a function of file (which is position of the filter arm).
    I = np.zeros(NumFiles)
    E = np.zeros(NumFiles)
    twotheta = np.zeros(NumFiles)
    chi = np.zeros(NumFiles)
    xcoord = np.zeros(NumFiles)
    ycoord = np.zeros(NumFiles)

    # Loop through all the filter positions and populate the I vector.
    for i in range(1,NumFiles+1):

        FileName = 'results_%0.5d.IND'%i
        try:
            #R = pickle.load(open(FileName+'.pkl', 'rb'))
            R = Rarray[FileName]
        except:
            # Read in the indexation file.
            #with open('results_00001.IND', 'r') as f:
            with open(FileName, 'r') as f:
                WholeFile = f.read()

            # Pull out the chunk of the file that contains the indexation table (starts with number of indexed reflections and ends with the deviatoric stuff.
            s = re.search('(number of indexed reflections:      [0-9]*?\r\n)([a-zA-Z0-9\s\(\)_\.-]*)( dev1, dev2)', WholeFile)
            ReflStr = s.group(2)

            # Nobu has a typo in his files, so two columns are accidentally blended together.  Fix it.
            ReflStr = ReflStr.replace('chi(deg)intensity', 'chi(deg) intensity')

            # Now turn the text into a named numpy array.
            ReflStr = StringIO.StringIO(ReflStr)
            R = np.genfromtxt(ReflStr, names=True)
            #pickle.dump(R, open(FileName+'.pkl', 'wb'))
            Rarray[FileName] = R

        # Sort by hkl
        R.sort(order=('h', 'k', 'l'))

        # Find one reflection
        r = R[(R['h']==hkl[0]) & (R['k']==hkl[1]) & (R['l']==hkl[2])]
        # Show it's values.
        #print r['h'], r['k'], r['l'], r['EnerkeV'], r['intensity']

        I[i-1] = r['intensity']
        E[i-1] = r['EnerkeV']
        twotheta[i-1] = r['2thetadeg']
        chi[i-1] = r['chideg']
        xcoord[i-1] = r['xexp']
        ycoord[i-1] = r['yexp']


    if not quiet:
        plt.plot(I)

    # New method ignores the overall slopes in the plateaus (whose physics is still not clear) and just uses the jumps across filters.
    Intensity0 = I[15:18].mean()
    Delta1 = Intensity0 - I[22:25].mean()
    Delta2 = I[54:57].mean() - I[61:64].mean()
    Delta3 = I[87:90].mean() - I[95:98].mean()
    Intensity1 = Intensity0-Delta1
    Intensity2 = Intensity1-Delta2
    Intensity3 = Intensity2-Delta3

    # # Original method using the averages of each plateau.  It assumes flat plateaus.
    # Intensity0 = I[:19].mean()
    # Intensity1 = I[22:57].mean()
    # Intensity2 = I[62:91].mean()
    # Intensity3 = I[96:147].mean()

    print '\nReflection (%d,%d,%d) with energy %g has intensities:' % (hkl[0], hkl[1], hkl[2], E.mean())
    print 'No filter:     %g' % Intensity0
    print 'One filter:    %g' % Intensity1
    print 'Two filters:   %g' % Intensity2
    print 'Three filters: %g' % Intensity3

    return(np.array([Intensity0, Intensity1, Intensity2, Intensity3]), np.mean(E)*1000, np.mean(twotheta), np.mean(chi), np.mean(xcoord),
           np.mean(ycoord))

if __name__ == '__main__':
    #hkl = np.array([-3, 3, -3])
    #hkl = np.array([-2, 4, -2])
    hkl = np.array([-5, 5, -3])

    print PlotValues(hkl)
