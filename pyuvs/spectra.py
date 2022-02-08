"""This module provides functions to work with spectra.
"""
import warnings
import numpy as np
import statsmodels.api as sm
from pyuvs.anc import load_muv_wavelength_center, \
    load_muv_sensitivity_curve_observational, load_template_no_nightglow, \
    load_template_co2_plus_uvd, load_template_co_cameron_bands, \
    load_template_solar_continuum
from pyuvs.constants import pixel_omega, kR
from pyuvs.data_files.contents import L1bFile, L1bFileCollection


with warnings.catch_warnings():
    warnings.simplefilter('ignore')


def load_standard_fit_templates() -> np.ndarray:
    """Load the standard fit templates (NO, aurora, solar)

    Returns
    -------
    np.ndarray
        The fit templates.

    """
    return np.vstack(
        [load_template_no_nightglow(),
         load_template_co_cameron_bands() + load_template_co2_plus_uvd(),
         load_template_solar_continuum()])


def rebin_templates(template, spectral_pixel_bin_width) -> np.ndarray:
    """Rebin a 1024 pixel template to match a given spectral bin width.

    Parameters
    ----------
    template
    spectral_pixel_bin_width

    Returns
    -------
    np.ndarray
        Rebinned spectral template.

    """
    reshaped_templates = \
        np.reshape(template, (template.shape[0],
                              int(template.shape[1]/spectral_pixel_bin_width),
                              spectral_pixel_bin_width))
    return np.sum(reshaped_templates, axis=-1)


def pad_spectral_axis_with_nan(
        array: np.ndarray, start_ind: int, n_wavelengths: int) -> np.ndarray:
    """Pad the spectral axis with NaNs.

    This is best described with an example. IUVS often takes data with 4
    bins/pixel, so it uses the 256 binning scheme. However, it only had the
    bandwidth to transmit 40 spectral bins within the range. This places the
    40 bins of data within a 256 bin array.

    Parameters
    ----------
    array: np.ndarray
        The spectral array (probably a detector image)
    start_ind: int
        The starting index of the
    n_wavelengths: int
        The number of wavelengths.

    Returns
    -------
    np.ndarray
        The input array with NaNs padded on the ends.

    """
    temp_array = np.zeros((array.shape[0], array.shape[1], n_wavelengths))\
                 * np.nan
    temp_array[..., start_ind:start_ind+array.shape[-1]] = array
    return temp_array


def rebin_wavelengths(
        wavelengths: np.ndarray, spectral_pix_bin_width: int) -> np.ndarray:
    """Rebin the wavelengths to a given bin width.

    Parameters
    ----------
    wavelengths: np.ndarray
        The wavelengths
    spectral_pix_bin_width: int
        The spectral bin width

    Returns
    -------
    np.ndarray
        Rebinned wavelengths.

    """
    return wavelengths.reshape((int(wavelengths.shape[0]/spectral_pix_bin_width),
                                spectral_pix_bin_width)).mean(axis=1)


def calculate_calibration_curve(
        spatial_bin_width: int, detector_sensitivity_curve: np.ndarray,
        wavelength_width: np.ndarray, voltage_gain: float,
        integration_time: float) -> np.ndarray:
    """Calculate the calibration curve [DN/kR].

    Parameters
    ----------
    spatial_bin_width: int
        The spatial bin width [pixels].
    detector_sensitivity_curve: np.ndarray
        The detector sensitivity curve.
    wavelength_width: np.ndarray
        The wavelength width.
    voltage_gain: float
        The voltage gain [V]
    integration_time: float
        The integration time.

    Returns
    -------
    np.ndarray
        The calibration curve.
    """
    bin_omega = pixel_omega * spatial_bin_width
    return wavelength_width * voltage_gain * integration_time * kR * \
        detector_sensitivity_curve * bin_omega


def fit_templates_to_nightside_data(fc: L1bFileCollection) -> np.ndarray:
    """Use multiple linear regression (MLR) to fit templates to nightside data.

    Parameters
    ----------
    fc: L1bFileCollection
        Collection of files.

    Returns
    -------
    np.ndarray
        The fitted brightnesses of NO and aurora. This array has shape (2,
        n_integrations, n_positions). Index 0 is NO; index 1 is aurora.

    """
    # Get data from the files. Assume nightside settings are the same each file
    fc.dayside = False
    dds = fc.stack_detector_image_dark_subtracted()
    dn_unc = fc.stack_detector_image_random_uncertainty_dn()
    file = fc.get_first_nightside_file()

    spectral_pixel_bin_width = int(np.median(file.binning.spectral_pixel_bin_width))
    starting_spectral_index = int(file.binning.spectral_pixel_bin_width[0] / spectral_pixel_bin_width)
    spatial_pixel_bin_width = int(np.median(file.binning.spatial_pixel_bin_width))
    wavelength_width = np.median(file.observation.wavelength_width)
    voltage_gain = file.observation.voltage_gain
    integration_time = file.observation.integration_time

    # Load in miscellaneous info
    wavelength_center = load_muv_wavelength_center()
    rebinned_wavelengths = rebin_wavelengths(wavelength_center,
                                             spectral_pixel_bin_width)
    rebinned_sensitivity_curve = np.interp(rebinned_wavelengths,
                                           load_muv_sensitivity_curve_observational()[
                                           :, 0],
                                           load_muv_sensitivity_curve_observational()[
                                           :, 1])
    rebinned_calibration_curve = calculate_calibration_curve(
        spatial_pixel_bin_width, rebinned_sensitivity_curve, wavelength_width,
        voltage_gain, integration_time)

    # Rebin the templates to match the data binning and stack them and add constant
    fit_templates = load_standard_fit_templates()
    rebinned_templates = rebin_templates(fit_templates,
                                         spectral_pixel_bin_width).T
    templates = sm.add_constant(rebinned_templates)

    # Pad nans
    '''We have now taken our 40 bin spectrum and placed it in its original 
    position within a 256 bin spectrum so we can fit it to the 256 bin template
    '''
    spectra = pad_spectral_axis_with_nan(dds, starting_spectral_index, 256)
    uncertainty = pad_spectral_axis_with_nan(dn_unc, starting_spectral_index,
                                             256)

    brightnesses = np.zeros((2,) + dds[:, :, 0].shape)
    for f in range(brightnesses.shape[1]):
        for g in range(brightnesses.shape[2]):
            fit = sm.WLS(spectra[f, g, :], templates,
                         weights=1 / uncertainty[f, g, :] ** 2,
                         missing='drop').fit()  # This ignores NaNs
            coeff = fit.params
            no_brightness = np.sum(coeff[1] * templates[:, 1] * wavelength_width / rebinned_calibration_curve)
            aurora_brightness = np.sum(coeff[2] * templates[:, 2] * wavelength_width / rebinned_calibration_curve)
            brightnesses[0, f, g] = no_brightness
            brightnesses[1, f, g] = aurora_brightness

    return brightnesses
