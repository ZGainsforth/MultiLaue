# Created 2016, Zack Gainsforth
from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
import QuickPlot

Err = np.array([1.95,
0.27,
32.59,
11.97,
1.58,
0.24,
2.44,
1.27,
0.86,
12.71,
0.98,
1.84,
2.08,
2.00,
4.51,
4.13,
2.93,
0.74,
0.58,
2.36,
0.29,
1.23,
3.17,
10.38,
20.93,
5.35,
1.78,
4.80,
1.87,
19.57,
1.46,
1.92])


E = np.array([12230,
11650,
10950,
9460,
14290,
16070,
14030,
17980,
15530,
9450,
15520,
12730,
18710,
17910,
20990,
20130,
18420,
13490,
17210,
22140,
16270,
17900,
17830,
23240,
26000,
18030,
18960,
19260,
19170,
26000,
20150,
21580])

print ("%% rel error mean = %0.02f and standard deviation: %0.02f" % (np.mean(Err), np.std(Err)))

11000, 23000

Keepers = (E>11000) & (E<23000)
print Keepers

print ("%% rel error mean = %0.02f and standard deviation: %0.02f in region 11-23 keV" % (np.mean(Err[Keepers]), np.std(Err[Keepers])))


Fraw = np.genfromtxt('../Beamline Characteristics/whitebeamflux.txt', skip_header=1)
Fraw[:,1] /= max(Fraw[:,1])/35

fig, ax = QuickPlot.SpecPlot(Fraw, boldlevel=3, title='Flux curve compared with errors', xlabel='eV', ylabel='Points: % relative error\nCurve: flux (arbitrary units)')
QuickPlot.QuickPlot(E,Err, figax=(fig,ax), plottype='scatter', boldlevel=5)
plt.legend(['Flux Curve', 'Error of best fit values'])
plt.show()
