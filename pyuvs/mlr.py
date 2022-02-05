"""This module provides functions to help perform an MLR fit.

MLR = multiple linear regression.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from pyuvs.anc import load_muv_wavelength_center, \
    load_muv_sensitivity_curve_observational, load_template_no_nightglow, \
    load_template_co2p_uvd, load_template_co_cameron_bands, \
    load_template_solar_continuum
from pyuvs.constants import pixel_omega, kR
from pyuvs.data_files0 import find_latest_apoapse_muv_file_paths_from_block, \
    L1bFile


def load_standard_fit_templates() -> np.ndarray:
    """Load the standard fit templates (NO, aurora, solar)

    Returns
    -------

    """
    return np.vstack([load_template_no_nightglow(),
                      load_template_co_cameron_bands() + load_template_co2p_uvd(),
                      load_template_solar_continuum()])


def rebin_templates(temp, spectral_pix_bin_width) -> np.ndarray:
    reshaped_templates = \
        np.reshape(temp, (temp.shape[0], int(temp.shape[1]/spectral_pix_bin_width),
                          spectral_pix_bin_width))
    return np.sum(reshaped_templates, axis=-1)


def pad_spectral_axis_with_nan(array, start_ind, n_wavelengths):
    temp_array = np.zeros((array.shape[0], array.shape[1], n_wavelengths)) * np.nan
    temp_array[..., start_ind:start_ind+array.shape[-1]] = array
    return temp_array


def rebin_wavelengths(wavelengths, spectral_pix_bin_width):
    return wavelengths.reshape((int(wavelengths.shape[0]/spectral_pix_bin_width), spectral_pix_bin_width)).mean(axis=1)


def calculate_calibration_curve(spatial_bin_width, detector_sensitivity_curve, wavelength_width, voltage_gain, integration_time):
    """DN/kR"""
    bin_omega = pixel_omega * spatial_bin_width
    return wavelength_width * voltage_gain * integration_time * kR * detector_sensitivity_curve * bin_omega


if __name__ == '__main__':
    import time
    t0 = time.time()
    # Find all files
    p = Path('/media/kyle/Samsung_T5/IUVS_data')
    files = find_latest_apoapse_muv_file_paths_from_block(p, 4000)
    files = [L1bFile(f) for f in files]

    # Load in a nightside file
    file = files[2]
    dds = np.vstack([f.detector_dark_subtracted for f in files if not f.is_dayside_file()])
    dnunc = np.vstack([f.random_uncertainty_dn for f in files if not f.is_dayside_file()])
    # Get info from the test file
    spectral_pixel_bin_width = int(np.median(file.binning.spectral_pixel_bin_width))
    starting_spectral_index = int(file.binning.spectral_pixel_bin_width[0] / spectral_pixel_bin_width)
    spatial_pixel_bin_width = int(np.median(file.binning.spatial_pixel_bin_width))
    wavelength_width = np.median(file.observation.wavelength_width)
    voltage_gain = file.observation.mcp_gain
    integration_time = file.observation.integration_time

    # Load in miscellaneous info
    wavelength_center = load_muv_wavelength_center()
    rebinned_wavelengths = rebin_wavelengths(wavelength_center, spectral_pixel_bin_width)
    rebinned_sensitivity_curve = np.interp(rebinned_wavelengths, load_muv_sensitivity_curve_observational()[:, 0],
                                           load_muv_sensitivity_curve_observational()[:, 1])
    rebinned_calibration_curve = calculate_calibration_curve(
        spatial_pixel_bin_width, rebinned_sensitivity_curve, wavelength_width,
        voltage_gain, integration_time)

    # Rebin the templates to match the data binning and stack them and add constant
    fit_templates = load_standard_fit_templates()
    rebinned_templates = rebin_templates(fit_templates, spectral_pixel_bin_width).T
    templates = sm.add_constant(rebinned_templates)

    # Pad nans
    '''We have now taken our 40 bin spectrum and placed it in its original 
    position within a 256 bin spectrum so we can fit it to the 256 bin template
    '''
    spectra = pad_spectral_axis_with_nan(dds, starting_spectral_index, 256)
    uncertainty = pad_spectral_axis_with_nan(dnunc, starting_spectral_index, 256)
    t1 = time.time()
    foo = np.zeros(dds[:, :, 0].shape)
    for f in range(foo.shape[0]):
        for g in range(foo.shape[1]):
            fit = sm.WLS(spectra[f, g, :], templates, weights=1/uncertainty[f, g, :]**2, missing='drop').fit()   # This ignores NaNs
            coeff = fit.params

            no_brightness = np.sum(coeff[1] * templates[:, 1] * wavelength_width / rebinned_calibration_curve)
            #print(no_brightness)
            foo[f, g] = no_brightness
    t2 = time.time()
    print(t2-t1, t1-t0)
    fig, ax = plt.subplots()
    ax.imshow(foo, vmin=0, vmax=4)
    plt.savefig('/home/kyle/junk.png')
