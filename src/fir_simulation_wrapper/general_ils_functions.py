"""GENERAL_ILS_FUNCTIONS 

General functions to do with the ILS.

Author: Sanjeevani Panditharatne
"""

import numpy as np
from scipy.fftpack import fft, ifft
from scipy.interpolate import interp1d
from scipy.io import readsav
import xarray as xr


def process_spectrum_general(
    frequency,
    radiance,
    fre_grid,
    st,
    ed,
    new_pd,
    apodisation_func=False,
    test_delta=False,
):
    """Apply the optical path difference to a spectrum using a boxcar function or a triangle apodisation function to a high resolution spectrum.
    Formerly called apodised_spectrum.
    Name changed to avoid confusion for FINESSE which requires a spectrally depdendent ILS applied.

    Adapted from apodise_spectra_boxcar_v1.pro
    ;
    ; Original Author: J Murray (14-Oct-2020)
    ;
    ; Additional comments by R Bantges
    ; Version 1: Original
    ;
    Params
    ------
    frequency array
        Original wavenumber scale (cm^-1)
    radiance array
        Original spectrum
    fre_grid float
        The frequency of the output grid for the apodised spectra (cm^-1)
    st float
        Wavenumber to start apodised spectrum (cm^-1)
    ed float
        Wavenumber to end apodised spectrum (cm^-1)
    new_pd float
        Optical path difference i.e. width of boxcar to apodise (cm)
    apodisation_func string
        deafult=False
        Function to use in addition to boxcar to apodise the spectrum
        Options
        -------
        "triangle" - Triangle function, running from 1 at centre of interferogram
        to zero at edge of interferogram
    test_delta bool
        deafult=False
        If True, the spectrum is taken to be a delta function, can be
        used to test the apodisation. This should return the ILS which is a sinc
        function in the case of a boxcar
        If False input spectrum is used

    Returns:
    -------
    wn array
        Wavenumber of apodised spectrum (cm^-1)
    radiance array
        Radiance or transmission of apodised spectrum
        (same units as input)

    Author: Sanjeevani Panditharatne and Laura Warwick
    """
    # Determine the number of samples making up the output spectra
    samples = int(np.round((ed - st) / fre_grid))

    # Define the wavenumber grid resolution (Fixed high resolution grid.
    # The Monochromatic spectra will be interpolated onto this grid for
    # convenience and potentially reduce time taken for the FFT, the arbitrary
    # number of points in the spectra can be such that it significantly slows
    # the FFT.
    # NB: 0.0001 cm-1 was chosen to resolve the spectral features in the
    # high resolution simulation
    dum_new_res = 0.0001
    dum_samples = int(np.round((ed - st) / dum_new_res))
    # The number of samples in the high res frequency scale

    # ********** Define the arrays for the re-interpolated radiance files **********
    # generate a wavenumber scale running from st - ed wavenumbers
    # at new_res cm-1
    new_fre = np.arange(st, ed, fre_grid)
    # generate a wavenumber scale running from st - ed wavenumbers at 0.001 cm-1
    dum_new_fre = np.arange(st, ed, dum_new_res)
    # ******************************************************************************

    # ********** Interpolate the high res radiance to new array scales **********
    f_dum_spec = interp1d(frequency, radiance)
    dum_spec = f_dum_spec(dum_new_fre)
    if test_delta:
        dum_spec = np.zeros_like(
            dum_spec
        )  # These can be set to produce a delta function to check the sinc
        dum_spec[int(15000000 / 2) : int(15000000 / 2) + 101] = 100.0
    # *****************************************************************************

    # FFT the interpolated LBLRTM spectrum
    int_2 = fft(dum_spec)
    # sampling=1./(2*0.01)/samples/100.   # Sampling interval of the interferogram in cm these are the same for the 0.001 and 0.01 spectra
    sampling = 1.0 / (2 * fre_grid) / samples / 100.0
    # Sampling interval of the interferogram in cm these are the same for the 0.001 and 0.01 spectra

    # ********** Apodise the LBLRTM sim and transform **********
    Q = int(
        round(new_pd / 100.0 / sampling / 2.0)
    )  # number of samples required to extend the path difference to 1.26cm
    # *****************************************************************************

    # Define an array to hold the folded out inteferogram
    int_1 = np.zeros(samples, dtype=np.cdouble)

    # 'int_2' - this interferogram is equivalent to a sampling grid of 0.001 cm-1
    # in the spectral domain, this statement applies a boxcar apodisation over +/-1.26 cm
    int_2[Q:-Q] = 0.0

    # The following two lines reduce the output spectra to a sampling grid of 0.01 cm-1
    # while copying in the truncated interferogram from the high resolution interferogram
    int_1[0 : int(round(samples / 2))] = int_2[0 : int(round(samples / 2))]
    int_1[int(round(samples / 2)) : samples] = int_2[
        (dum_samples) - int(round(samples / 2)) : dum_samples
    ]

    if apodisation_func == "triangle":
        print("Applying triangle")
        int_1_unapodised = np.copy(int_1)
        triangle_left = [1, 0]
        triangle_left_x = [0, Q]
        triangle_left_x_all = np.arange(len(int_1[0:Q]) + 1)
        f_triangle_left = interp1d(triangle_left_x, triangle_left)
        triangle_right = [0, 1]
        triangle_right_x = [len(int_1) - Q - 1, len(int_1)]
        triangle_right_x_all = np.arange(len(int_1) - Q - 1, len(int_1), 1)
        f_triangle_right = interp1d(triangle_right_x, triangle_right)

        int_1[0 : Q + 1] = int_1[0 : Q + 1] * f_triangle_left(triangle_left_x_all)
        int_1[-Q - 2 : -1] = int_1[-Q - 2 : -1] * f_triangle_right(triangle_right_x_all)

    elif not apodisation_func:
        print("Applying boxcar")

    else:
        print("No recognised function selected, defaulting to boxcar")

    new_lbl_spec = ifft(int_1)

    # ***********************************************************************
    apodised_spectra = np.real(new_lbl_spec / (fre_grid / dum_new_res))
    return new_fre, apodised_spectra

