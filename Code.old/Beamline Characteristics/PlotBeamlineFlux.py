# Created 2016, Zack Gainsforth
import matplotlib
#matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import numpy as np
import QuickPlot as QuickPlot

mamflux = np.genfromtxt('12.3.2_flux_after extrapolated.txt')
QuickPlot.SpecPlot(mamflux, title='Whitebeam flux from Matt.', xlabel='eV', ylabel='photons/sec')

whiteflux = np.genfromtxt('whitebeamflux.txt')
QuickPlot.SpecPlot(whiteflux, title='Whitebeam flux from Nobu.', xlabel='eV', ylabel='photons/sec')

def raise_window(figname=None):
    if figname:
        plt.figure(figname)
        cfm = plt.get_current_fig_manager()
        cfm.window.activateWindow()
        cfm.window.raise_()

raise_window()
plt.show()