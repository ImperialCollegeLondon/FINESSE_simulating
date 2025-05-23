"""FSI

This module contains code to apply the ILS and other useful things can be included.

Within RTTOV the FSI ILS is modelled used the strong Norton-Beer Apodisation

Author: Sanjeevani Panditharatne
"""

import numpy as np
import xarray as xr
import os

def rttov_forum_apodise(wn,spec):
    """Apply ILS to a spectrum

    Args:
        spec (array): spectrum
        wn (array): wn scale of spectrum (cm-1)
        wn_min (array): spectrum
    """

    wn_min = min(wn)
    wn_max = max(wn)
    
    nbs_wv, nbs_fl = np.loadtxt(os.environ['FIR_AUX_PATH']+'FORUM_RTTOV_ISRF.txt', unpack = True)
    
    #interpolate instrument line shape onto same freq scale (same gap between wn) - from -3 to -3
    #convultion specrum then instrument line shape - mode = same - normalised after, dvided by sum of instrument
    #line shape
    
    apodise = xr.Dataset(
    {'ils':( ('wn'), nbs_fl)},
    coords = {"wn" : nbs_wv}) #the resolution
    
    print('WN limits are fixed to [100,1600,0.3]')
    
    rttov_wn = [100+i*0.3 for i in range(5001)]
    res = 0.001
    
    xarray = xr.Dataset(
    {'spec':( ('wn'), spec)},
    coords = {"wn" : wn})
    
    new_spec =  xarray.interp(wn=np.round(np.arange(wn_min,wn_max+res,res),3))
    
    convolved = np.convolve(apodise.ils.values, new_spec.spec.values, mode = 'same')
    convolved_norm = convolved/(sum(apodise.ils.values))
    
    # Interpolate onto RTTOV sampling
    LBL_forum_apod =  xr.Dataset(
    {'spec':( ('wn'), convolved_norm)},
    coords = {"wn" : new_spec.wn.values}).interp(wn=rttov_wn)
    
    return LBL_forum_apod.wn.values, LBL_forum_apod.spec.values
