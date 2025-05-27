"""
Functions for use in working with observational instruments.
(SP) No edits made to functions except adjustment of ISRF path. Function in_range taken from BP util.py file.

Author: Ben Pery
Edited: Sanjeevani Panditharatne
"""

import numpy as np
import xarray as xr
from scipy.integrate import trapezoid
from scipy.interpolate import interp1d
from scipy.fftpack import fft, ifft
import os

def in_range(array, range, incl=False):
    """
    Returns a boolean array which is True for the members of array within the bounds specified by range.
    
    Arguments:
        :array:      numerical array
        :range:      list or tuple 
        :incl:       if True, inequalities are inclusive. Default is False
    Returns:
        numpy.ndarray 
    """

    if incl:
        return np.logical_and(range[0] <= array, array <= range[1])
    else:
        return np.logical_and(range[0] < array, array < range[1])


def apply_srf(radiance, spec_basis, srf):
    """
    Applies spectral response function for a radiometer-type instrument with spectral basis v:
        channel radiance = integral( srf(v) * radiance(v) )dv / integral srf(v) dv
    """

    integrated_radiance = trapezoid(srf * radiance, spec_basis)
    normalisation = trapezoid(srf, spec_basis)
    channel_radiance = np.divide(integrated_radiance, normalisation)

    return channel_radiance


def prefire_simulation(spec, wn, inst, spec_range=(100,1600), sc=0, reject_mask=0b000011, verbose=False):
    """
    Applies PREFIRE TIRS1/2 spectral response functions to a high-resolution atmospheric radiance simulation.

    spec        : spectrum of input simulation, in units of W / (cm2 sr cm-1)-1
    wn          : wavenumbers of the input simulation, in units of cm-1
    inst        : string 'TIRS1' or 'TIRS2' as appropriate
    spec_range  : spectral range (units cm-1) of input simulation (SRFs not applied for channels outs of this range)
    sc          : int (0-7) indicating which sensor array to simulate (SRFs should be identical across sc, but 
                channels with noise or quality flag issues will be masked)
    reject_mask : binary mask indicating which flags to reject (1) or let pass (0) when calculating SRFs and noise.
                see code below to determine which bits to flag
    verbose     : boolean option for outputting more information about each channel as scanned

    output_ds   : xarray Dataset object containing variables channel_radiance and NEDR_wn, added to
                noise characteristics original to the SRF file.
    """

    # QC filtering options
    flag_descriptors = ['is masked',                                                    # b0
                        'has extreme noise or is unresponsive',                         # b1
                        'is in greater-noise category',                                 # b2
                        'has unreliable calibration due to stray light contribution',   # b3
                        'has unreliable calibration due to thermal effects',            # b4
                        'has unreliable calibration due to filter edge effects']        # b5
    # bit numbers    b543210 
    # reject_mask = 0b000011

    srf_filepath = os.environ['FIR_AUX_PATH']+'PREFIRE_' + str(inst) + '_SRF_v13_2024-09-15.nc'

    tirs_srf = xr.load_dataset(srf_filepath)
    n_ch = tirs_srf.channel.size

    # quality filtering, rejecting channels & scenes with specified flags
    channel_masks = tirs_srf['detector_bitflags'][:,sc].data.astype(int)
    channels_to_reject_flagged = np.where(channel_masks & reject_mask)[0]

    # verbose output for channel-by-channel diagnostics
    if verbose:

        bits = 2**np.arange(6)
        bitflag_dict = dict(zip(bits,flag_descriptors))

        for ch, mask in enumerate(channel_masks):

            has_flags = mask > 0

            if has_flags:
                reject_channel = mask & reject_mask

                flags = [mask & 2**bit for bit in range(6)]
                print(f'Channel {ch} detector ' + ', '.join([bitflag_dict[flag] for flag in flags if flag != 0]) + '.')
                if reject_channel:
                    print(f'Channel {ch} excluded.')


    # wavenumber filtering, rejecting channels which lie outside of simulation range
    channels_to_reject_spectral = np.where(   # could just use an OR here 
        np.logical_not(
            np.logical_and(spec_range[0] < tirs_srf['channel_wavenum1'][:,sc].data,
                        tirs_srf['channel_wavenum2'][:,sc].data < spec_range[1])
                        ))[0]

    # combining QC and wavenumber filtering to define rejection list
    channels_to_reject = list(set(np.append(channels_to_reject_flagged, channels_to_reject_spectral)))
    channels_to_reject.sort()

    # creating wavenumber spectrum and selecting spectral range
    wnums_tirs = 1.e4 / tirs_srf.wavelen.data  # conversion of spectrum in µm to cm-1
    longwave_selection = in_range(wnums_tirs, spec_range)
    wnums_tirs = wnums_tirs[longwave_selection][::-1]

    # calculating TIRS NEDR conversion from W/(m2 sr µm) to mW/(m2 sr cm-1)
    NEDR_wnum = 1.e3 * np.divide(tirs_srf.channel_mean_wavelen.data, tirs_srf.channel_mean_wavenum.data) * tirs_srf.NEDR

    # variables for saving later from SRF
    srf_vars = [var for var in tirs_srf.variables]
    vars_to_keep = ['channel_wavelen1',
                    'channel_wavelen2',
                    'channel_wavenum1',
                    'channel_wavenum2',
                    'channel_center_wavelen',
                    'channel_center_wavenum',
                    'channel_mean_wavelen',
                    'channel_mean_wavenum',
                    'detector_bitflags',
                    'NEDR',]
    vars_to_drop = [var for var in srf_vars if var not in vars_to_keep]
    vars_1d = ['channel_wavelen1',
                'channel_wavelen2',
                'channel_wavenum1',
                'channel_wavenum2',
                'channel_center_wavelen',
                'channel_center_wavenum',
                'channel_mean_wavelen',
                'channel_mean_wavenum',]

    # make correctly-sized arrays for radiative transfer results
    rt_spec_range = in_range(wn, (np.max([np.min(wnums_tirs),spec_range[0]]), spec_range[1]))
    wnums_radtran = wn[rt_spec_range]
    radiances_radtran = 1.e7 * spec[rt_spec_range]  # conversion of radiance from W/cm2 to mW/m2

    # loop over channels to calculate radiances
    channel_radiances = np.zeros(n_ch)
    for ch in range(n_ch):
        if ch not in channels_to_reject:
            srf_radtran_res = np.interp(wnums_radtran, wnums_tirs, tirs_srf['srf'][:,ch,sc].data[longwave_selection][::-1])
            channel_radiances[ch] = apply_srf(radiances_radtran, wnums_radtran, srf_radtran_res)

    # Dataset to return as netcdf
    output_ds = tirs_srf.copy().drop_vars(vars_to_drop)
    for var_1d in vars_1d:
        output_ds[var_1d] = output_ds[var_1d].sel(scene=0, drop=True)
    
    # storing variables
    output_ds['channel_radiance'] = (['channel',], channel_radiances)
    output_ds['channel_radiance'] = output_ds.channel_radiance.assign_attrs({
        'units':'mW / (m2 sr cm-1)',
        'long_name':'Simulated spectral radiance at channel',
    })

    output_ds['NEDR_wn'] = (['channel', 'scene',], NEDR_wnum.data)
    output_ds['NEDR_wn'] = output_ds.NEDR_wn.assign_attrs({
        'units':'mW / (m2 sr cm-1)',
        'long_name':'Noise equivalent delta radiance, converted'
    })

    # assigning information attributes to the dataset
    output_ds = output_ds.assign_attrs({
        'description':'Simulations of PREFIRE radiances from LBLRTM calculations',
        'SRF_distributed_file':'PREFIRE_' + inst + '_SRF_v13_2024-09-15.nc',
    })

    return output_ds