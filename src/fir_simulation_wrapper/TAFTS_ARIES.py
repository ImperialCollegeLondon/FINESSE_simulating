"""TAFTS_ARIES

This module contains code to apply the ILS and other useful things can be included. 
Based on the IDL code from Jonathan Murray.

Author: Sanjeevani Panditharatne
"""

import numpy as np
from scipy.fftpack import fft, ifft
from scipy.interpolate import interp1d
import xarray as xr
import os

def ARIES_apod(wn,spec, vmin, vmax):
    """Apply ILS to a spectrum

    Args:
        wn (array): wn scale of spectrum (cm-1)
        spec (array): spectrum
        vmin (float): minimum wn - better to define specifically
        vmax (float): maximum wn
    """

    xarray = xr.Dataset(
    {'spec':( ('wn'), spec)},
    coords = {"wn" : wn})
    new_res = 0.1
    samples=round((vmax-vmin)/new_res)
    new_fre = np.linspace(vmin,vmax,samples)
    NEW_L=1./(2*new_res)
    sampling=NEW_L/samples/100.
    # print('sampling and samples ',sampling,samples)
    data = xarray.interp(wn = new_fre)
    normalised = np.int16(data.spec.values / max(data.spec.values)*32767)
    int2 = fft(normalised)

#   ;******************************************* Apodise the LBLRTM sim and transform *******************************************************

    path_diff=0.5/0.01  # ;L=1/(2*delta_sigma)
    aries_pd=0.01 # ; 1 cm
    Q=round(aries_pd/sampling/2.)  # ;number of samples required to extend the path difference to 1cm

    int2[Q:samples-1-Q]=0.

    new_spec=ifft(int2)
    norm_new_sig = new_spec / 32767

    xr_sim_aries_apod = xr.Dataset(
        {'Aries':( ('wn_aries'), norm_new_sig*max(data.spec.values))},
        coords = {"wn_aries" : new_fre})

    return xr_sim_aries_apod.wn_aries.values, xr_sim_aries_apod.Aries.values

""" """

def TAFTS_apod(wn,spec,vmin,vmax):
    """Apply ILS to a spectrum

    Args:
        wn (array): wn scale of spectrum (cm-1)
        spec (array): spectrum
        vmin (float): minimum wn - better to define specifically
        vmax (float): maximum wn
    """
    xarray = xr.Dataset(
    {'spec':( ('wn'), spec)},
    coords = {"wn" : wn})
    
    new_res = 0.01
    samples=round((vmax-vmin)/new_res)
    new_fre = np.linspace(vmin,vmax,samples)
    NEW_L=1./(2*new_res)
    sampling=NEW_L/samples/100.
    # print('sampling and samples ',sampling,samples)
    new_spec = xarray.interp(wn = new_fre)
     
#     ;******************************************* Call TAFTS apodisation function ***********************************************************

    interferogram = np.ones(65536) #Define an interferogram of 65536 samples and value unity

# ;***** OPEN AND READ IN THE TAFTS APODISATION FUNCTION *****

    kaiser40k_file = np.loadtxt(os.environ['FIR_AUX_PATH']+'K_10_40k.txt')


# ;***************************************************************************************************************************************
# ;******************************************* Multiply the TOPHAT with the kaiser function **********************************************
    interferogram[12768:32767]=interferogram[12768:32767]*kaiser40k_file[0:19999]
    interferogram[32768:52767]=interferogram[32768:52767]*kaiser40k_file[20000:39999]
    interferogram[0:12767]=0.
    interferogram[52768:65535]=0.

# ;***************************************************************************************************************************************

# The LBL simulations have been resampled onto a new_res cm-1 frequency scale. 
# This section resamples the kaiser function onto a spatial grid compatible with
# the FFT of the interpolated LBL spectra
    kai = np.array([a for a in range(0, 65536)]) # TAFTS has an interferogram sampling of 2.5312 microns, LBL "sampling" microns this line defines the
#                                                         ;number of points and extent of the kaiser function on the new interferogram sampling grid
    new_kai_1 =round(2.5312e-6/(2.*sampling)*65536)
    new_kai_2 = np.array([a for a in range(0,new_kai_1+1)])
    new_kai = new_kai_2/(2.5312e-6)*(2.*sampling)

#   Interpolate the TAFTS apodisation function onto the new grid scale

    apodise = xr.Dataset(
        {'interf':( ('kai'), interferogram)},
        coords = {"kai" : kai}).interp(kai=new_kai) 

#  Set the apodiation function sample extent
    Q=round(2.5312e-6/(2.*sampling)*65536/2)  

#   FFT THE interpolated LBL spectrum
    normalised = (np.int16(new_spec.spec.values / max(new_spec.spec.values)*32767))
    int2 = fft(normalised)


# ;******************************************* Apodise the LBLRTM sim and transform *******************************************************

    int2[0:Q-1]=int2[0:Q-1]*apodise.interf.values[Q:2*Q-1]
    int2[samples-1-(Q-1):samples-1]=int2[samples-1-(Q-1):samples-1]*apodise.interf.values[0:(Q-1)]
    int2[Q:samples-1-Q]=0.

    new_lbl_spec=ifft(int2)
    norm_new_sig_tafts = new_lbl_spec / 32767

    xarray_sim_tafts_apod = xr.Dataset(
        {'Tafts':( ('wn_tafts'), norm_new_sig_tafts*max(new_spec.spec.values))},
        coords = {"wn_tafts" : new_fre})

    return xarray_sim_tafts_apod.wn_tafts.values, xarray_sim_tafts_apod.Tafts.values