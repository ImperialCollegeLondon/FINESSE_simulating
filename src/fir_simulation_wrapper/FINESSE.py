"""FINESSE

This module contains code to apply the ILS and other useful things can be included.

A boxcar is first applied to a high resolution spectrum using the general function process_spectrum_general.
FINESSE has an OPD of 1.21
The instrument line shape is then applied using apply_ILS_sav.

Author: Sanjeevani Panditharatne
"""

import numpy as np
from scipy.fftpack import fft, ifft
from scipy.interpolate import interp1d
from scipy.io import readsav
import xarray as xr

from fir_simulation_wrapper.general_ils_functions import *

def apply_ILS_sav(ILS, wn, spectrum, pad_length=10):
    """Apply ILS to a spectrum

    Args:
        ILS (array (ILS, frequency bin)): ILS axis 0 is the
            ILS axis 1 is the frequency bin as defined by
            start_fre, end_fre
        wn (array): wn scale of spectrum (cm-1)
        spectrum (array): spectrum
        padlength (int): amount to add to end of each wavenumber
            section to remove edge effects. Expressed in units of
            wavenumber
    """
    print("Applying ILS sav file")

    # Here I have redefined the start and end fre such that it is an array, to get the bins
    # the function requires the inputs start_fre and end_fre to be arrays of wavenumber rather than float values
    start_fre = np.array(
        [
            360.0,
            450.0,
            560.0,
            630.0,
            730.0,
            850.0,
            950.0,
            1050.0,
            1150.0,
            1250.0,
            1360.0,
            1450.0,
            1550.0,
            1650.0,
            1750.0,
            1800.0,
            1900.0,
        ]
    )
    end_fre = np.append(start_fre[1:], 1950.0)

    # Specify frequency scale of ILS
    ILS_frequency_scale = np.linspace(-5, 5, np.shape(ILS)[0])

    # Loop through each chunk of spectrum and apply the ILS
    # to that chunk
    for i in range(len(start_fre)):
        # Trim to correct chunk of spectrum
        # Add extra for convolution overlap
        index = np.where(
            np.logical_and(
                wn >= start_fre[i] - pad_length,
                wn <= end_fre[i] + pad_length,
            )
        )
        wn_now = wn[index]
        if len(index[0]) > 0:
            spectrum_now = spectrum[index]
            # Interpolate ILS onto frequency of signal COMMENT OUT LINES BELOW
            ILS_frequency_scale_interp = np.arange(-5, 5, np.average(np.diff(wn_now)))
            ils_now_interp = np.interp(
                ILS_frequency_scale_interp, ILS_frequency_scale, ILS[:, i]
            )[::-1]
            # convolution below, REPLACED ILS_INTERP WITH WN_NOW

            spectrum_interp = np.convolve(
                spectrum_now,
                ils_now_interp,
                mode="same",
            ) / sum(ils_now_interp)

            # Trim so only spectrum in area of interest is retained
            index_out = index = np.where(
                np.logical_and(
                    wn_now >= start_fre[i],
                    wn_now < end_fre[i],
                )
            )

            wn_out = wn_now[index_out]
            spectrum_out = spectrum_interp[index_out]

            if i == 0:
                wn_all = wn_out
                spectrum_all = spectrum_out
            else:
                wn_all = np.append(wn_all, wn_out)
                spectrum_all = np.append(spectrum_all, spectrum_out)
        else:
            continue
    return wn_all, spectrum_all


def apply_ILS_nc(ILS_nc_path, wn, spectrum, pad_length=10):
    """Apply ILS to a spectrum but load it from netcdf file

    Args:
        ILS_nc_path (string): Load variables from netcdf file
        wn (array): wn scale of spectrum (cm-1)
        spectrum (array): spectrum
        padlength (int): amount to add to end of each wavenumber
            section to remove edge effects. Expressed in units of
            wavenumber
    """
    print("========== Applying FINESSE ILS ==========")

    # Load netcdf file
    ILS_ncdf = xr.open_dataset(ILS_nc_path)

    # Define variables
    start_fre = ILS_ncdf.lo_bound.values
    end_fre = ILS_ncdf.hi_bound.values

    # Specify frequency scale of ILS
    ILS_frequency_scale = ILS_ncdf.wn.values
    ILS = ILS_ncdf.ils.values
    # Loop through each chunk of spectrum and apply the ILS
    # to that chunk
    for i in range(len(start_fre)):
        # Trim to correct chunk of spectrum
        # Add extra for convolution overlap
        index = np.where(
            np.logical_and(
                wn >= start_fre[i] - pad_length,
                wn <= end_fre[i] + pad_length,
            )
        )
        wn_now = wn[index]
        spectrum_now = spectrum[index]
        # Interpolate ILS onto frequency of signal COMMENT OUT LINES BELOW
        ILS_frequency_scale_interp = np.arange(-5, 5, np.average(np.diff(wn_now)))
        ils_now_interp = np.interp(
            ILS_frequency_scale_interp, ILS_frequency_scale, ILS[:, i]
        )[::-1]
        # convolution below, REPLACED ILS_INTERP WITH WN_NOW

        spectrum_interp = np.convolve(
            spectrum_now,
            ils_now_interp,
            mode="same",
        ) / sum(ils_now_interp)

        # Trim so only spectrum in area of interest is retained
        index_out = index = np.where(
            np.logical_and(
                wn_now >= start_fre[i],
                wn_now < end_fre[i],
            )
        )

        wn_out = wn_now[index_out]
        spectrum_out = spectrum_interp[index_out]

        if i == 0:
            wn_all = wn_out
            spectrum_all = spectrum_out
        else:
            wn_all = np.append(wn_all, wn_out)
            spectrum_all = np.append(spectrum_all, spectrum_out)
    return wn_all, spectrum_all
