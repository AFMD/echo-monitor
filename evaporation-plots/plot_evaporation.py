#!/usr/bin/env python
#coding:utf-8
"""
  Author:   Ross <ross.warren@pm.me>
  Purpose:  Plot ECHO data
  Created:  23/05/19
"""

import pandas as pd
import matplotlib.pyplot as plt


def readcsv(csvfile):
    """Read csv produced from ECHO live stats."""
    df = pd.read_csv(csvfile, delimiter=',', header=0)
    return df


def plotStats(data):
    """Plots saved stats."""
    fig, axarr = plt.subplots(2, 2, figsize=(16, 8))

    # Chamber vent lines
    axarr[0, 0].axvline(x=78.65, color='black', alpha=0.6)
    axarr[0, 1].axvline(x=78.65, color='black', alpha=0.6)
    axarr[1, 0].axvline(x=78.65, color='black', alpha=0.6)
    axarr[1, 1].axvline(x=78.65, color='black', alpha=0.6)

    # Shutter opens lines
    axarr[0, 0].axvline(x=39.3, color='green', alpha=0.6)
    axarr[0, 1].axvline(x=39.3, color='green', alpha=0.6)
    axarr[1, 0].axvline(x=39.3, color='green', alpha=0.6)
    axarr[1, 1].axvline(x=39.3, color='green', alpha=0.6)

    # Shutter closes lines
    axarr[0, 0].axvline(x=46.4, color='red', alpha=0.6)
    axarr[0, 1].axvline(x=46.4, color='red', alpha=0.6)
    axarr[1, 0].axvline(x=46.4, color='red', alpha=0.6)
    axarr[1, 1].axvline(x=46.4, color='red', alpha=0.6)

    axarr[0, 0].set_title('Source Temperatures')
    axarr[0, 0].plot(data['Sample'] / 60, data['Temp 1'], '.', label='Channel 1')
    # axarr[0, 0].plot(data['Sample'] / 60, data['Temp 2'], '.', label='Channel 2')
    axarr[0, 0].plot(data['Sample'] / 60, data['Temp 3'], '.', label='Channel 3')
    axarr[0, 0].set_xlabel('Time [mins]')
    axarr[0, 0].set_ylabel('Temperature [C]')
    axarr[0, 0].grid()
    axarr[0, 0].legend()
    # Example how to twin plot on subfig.
    # axarr[0,0].rate = axarr[0,0].twinx()
    # axarr[0, 0].rate.plot(data['Sample'], data['Rate 1'], 'C1.', label='Rate')

    axarr[0, 1].set_title('Source Rates')
    axarr[0, 1].plot(data['Sample'] / 60, data['Rate 1'], '.', label='Channel 1')
    # axarr[0, 1].plot(data['Sample'] / 60, data['Rate 2'], '.', label='Channel 2')
    axarr[0, 1].plot(data['Sample'] / 60, data['Rate 3'], '.', label='Channel 3')
    axarr[0, 1].set_ylim(-0.2, 0.3)
    axarr[0, 1].set_xlabel('Time [mins]')
    axarr[0, 1].set_ylabel('Sublimation Rate [Angstrom/s]')
    axarr[0, 1].grid()
    axarr[0, 1].legend()

    axarr[1, 0].set_title('Film thickness')
    axarr[1, 0].plot(data['Sample'] / 60, data['Thick 1'], '.', label='Channel 1')
    # axarr[1, 0].plot(data['Sample'] / 60, data['Thick 2'], '.', label='Channel 2')
    axarr[1, 0].plot(data['Sample'] / 60, data['Thick 3'], '.', label='Channel 3')
    axarr[1, 0].set_xlabel('Time [mins]')
    axarr[1, 0].set_ylabel('Film thickness [nm]')
    axarr[1, 0].grid()
    axarr[1, 0].legend()

    axarr[1, 1].set_title('Pressure')
    axarr[1, 1].semilogy(data['Sample'] / 60, data['Pressure'], '.')
    axarr[1, 1].set_xlabel('Time [mins]')
    axarr[1, 1].set_ylabel('Chamber Pressure [mBar]')
    axarr[1, 1].set_ylim(3e-7, 1.18e-6)
    axarr[1, 1].grid()
    axarr[1, 1].legend()

    fig.tight_layout()
    plt.show()
    
def plotStatsPub(data):
    """Plots saved stats for publication."""
    import matplotlib as mpl
    mpl.use('pdf')    
    
    # -------------------------------------------------------------
    # FUNCTIONS FOR PUBLICATION PLOTTING
    # Size paramters
    width = 6.68
    height = (width / 1.618)      # golden ratio
    
    # Direct input
    plt.rcParams['text.latex.preamble'] = [r"\usepackage{lmodern}"]
    # Options
    params = {'text.usetex': True,
              'font.size': 10,
              'font.family': 'lmodern',
              'text.latex.unicode': True,
              }
    plt.rcParams.update(params)
    
    markerSize = 2
    
    fig, axarr = plt.subplots(2, 2, figsize=(16, 8))

    ## Chamber vent lines
    #axarr[0, 0].axvline(x=78.65, color='black', alpha=0.6)
    #axarr[0, 1].axvline(x=78.65, color='black', alpha=0.6)
    #axarr[1, 0].axvline(x=78.65, color='black', alpha=0.6)
    #axarr[1, 1].axvline(x=78.65, color='black', alpha=0.6)
    
    ## Shutter opens lines
    #axarr[0, 0].axvline(x=39.3, color='green', alpha=0.6)
    #axarr[0, 1].axvline(x=39.3, color='green', alpha=0.6)
    #axarr[1, 0].axvline(x=39.3, color='green', alpha=0.6)
    #axarr[1, 1].axvline(x=39.3, color='green', alpha=0.6)
  
    ## Shutter closes lines
    #axarr[0, 0].axvline(x=46.4, color='red', alpha=0.6)
    #axarr[0, 1].axvline(x=46.4, color='red', alpha=0.6)
    #axarr[1, 0].axvline(x=46.4, color='red', alpha=0.6)
    #axarr[1, 1].axvline(x=46.4, color='red', alpha=0.6)


    # axarr[0, 0].set_title('Source Temperatures')
    axarr[0, 0].plot(data['Sample'] / 60, data['Temp 1'], '.', label='Channel 1', markersize=markerSize)
    # axarr[0, 0].plot(data['Sample'] / 60, data['Temp 2'], '.', label='Channel 2', markersize=markerSize)
    axarr[0, 0].plot(data['Sample'] / 60, data['Temp 3'], '.', label='Channel 3', markersize=markerSize)
    axarr[0, 0].set_xlabel('Time [mins]')
    axarr[0, 0].set_ylabel('Temperature [C]')
    axarr[0, 0].tick_params('y', which='both', colors='k', direction='in')
    axarr[0, 0].tick_params('x', colors='k', direction='in')
    axarr[0, 0].grid()
    # axarr[0, 0].legend()
    # Example how to twin plot on subfig.
    # axarr[0,0].rate = axarr[0,0].twinx()
    # axarr[0, 0].rate.plot(data['Sample'], data['Rate 1'], 'C1.', label='Rate')

    # axarr[0, 1].set_title('Source Rates')
    axarr[0, 1].plot(data['Sample'] / 60, data['Rate 1'], '.', label='Channel 1', markersize=markerSize)
    # axarr[0, 1].plot(data['Sample'] / 60, data['Rate 2'], '.', label='Channel 2', markersize=markerSize)
    axarr[0, 1].plot(data['Sample'] / 60, data['Rate 3'], '.', label='Channel 3', markersize=markerSize)
    axarr[0, 1].set_ylim(-0.1, 0.1)
    axarr[0, 1].set_xlabel('Time [mins]')
    axarr[0, 1].set_ylabel('Rate [\AA/s]')
    axarr[0, 1].tick_params('y', which='both', colors='k', direction='in')
    axarr[0, 1].tick_params('x', colors='k', direction='in')
    
    axarr[0, 1].grid()
    # axarr[0, 1].legend()

    # axarr[1, 0].set_title('Film thickness')
    axarr[1, 0].plot(data['Sample'] / 60, data['Thick 1'] * 100, '.', label='Channel 1', markersize=markerSize)
    # axarr[1, 0].plot(data['Sample'] / 60, data['Thick 2'] * 100, '.', label='Channel 2', markersize=markerSize)
    axarr[1, 0].plot(data['Sample'] / 60, data['Thick 3'] * 100, '.', label='Channel 3', markersize=markerSize)
    axarr[1, 0].set_xlabel('Time [mins]')
    axarr[1, 0].set_ylabel('Thickness [nm]')
    axarr[1, 0].tick_params('y', which='both', colors='k', direction='in')
    axarr[1, 0].tick_params('x', colors='k', direction='in')

    axarr[1, 0].grid()
    axarr[1, 0].legend()

    # axarr[1, 1].set_title('Pressure')
    axarr[1, 1].semilogy(data['Sample'] / 60, data['Pressure'], '.', color='C3', markersize=markerSize)
    axarr[1, 1].set_xlabel('Time [mins]')
    axarr[1, 1].set_ylabel('Pressure [mBar]')
    axarr[1, 1].tick_params('y', which='both', colors='k', direction='in')
    axarr[1, 1].tick_params('x', colors='k', direction='in')
    #axarr[1, 1].set_ylim(2e-6, 8e-6)
    axarr[1, 1].grid()
    # axarr[1, 1].legend()

    fig.set_size_inches(width, height)
    fig.subplots_adjust(left=.08, bottom=.09, right=.98, top=.98, hspace=0.28, wspace=0.4)
    fig.savefig('/home/ross/physics/projects/98-ECHO/FIGURES/20190516-ECHO-LOG-alq3-pid.pdf', dpi=300)


if __name__ == "__main__":
    df = readcsv('/home/ross/physics/projects/98-ECHO/DATA/20190516-ECHO-LOG-alq3-pid.csv')
    plotStatsPub(df)
