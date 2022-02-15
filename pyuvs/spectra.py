"""This module provides functions to work with spectra.
"""
import numpy as np
import statsmodels.api as sm
from pyuvs import kR, load_muv_sensitivity_curve_observational, \
    load_muv_wavelength_centers, load_template_co_cameron, \
    load_template_co2_plus_uvd, load_template_no_nightglow, \
    load_template_solar_continuum, pixel_omega


def load_standard_fit_templates() -> np.ndarray:
    """Load the standard fit templates.

    The standard fit templates are:

    0. NO nightglow
    1. CO Cameron bands
    2. Ultraviolet doublet
    3. Solar continuum.

    These correspond to the first axis.

    Returns
    -------
    np.ndarray
        The fit templates.

    Notes
    -----
    This array has shape (4, 1024).

    """
    return np.vstack([load_template_no_nightglow(),
                      load_template_co_cameron(),
                      load_template_co2_plus_uvd(),
                      load_template_solar_continuum()])


def rebin_templates(template: np.ndarray, spectral_pixel_bin_width: int) \
        -> np.ndarray:
    """Rebin N spectral templates to match a given spectral bin width.

    Parameters
    ----------
    template: np.ndarray
        The spectral template to rebin. Must have a shape of (number of
        templates, spectral bins per template).
    spectral_pixel_bin_width: int
        The number of IUVS detector spectral pixels to rebin the template to.

    Returns
    -------
    np.ndarray
        Rebinned spectral template.

    Examples
    --------
    Rebin the NO nightglow template to use the 256 spectral bin scheme. This
    uses 4 pixels / spectral bin.

    >>> import pyuvs as pu
    >>> no_template = pu.load_template_no_nightglow()
    >>> rebin = pu.rebin_templates(no_template[None, :], 4)
    >>> rebin.shape
    (1, 256)

    """
    new_shape = (template.shape[0],
                 template.shape[1]//spectral_pixel_bin_width,
                 spectral_pixel_bin_width)
    reshaped_templates = np.reshape(template, new_shape)
    return np.sum(reshaped_templates, axis=-1)


def pad_spectral_image_with_nan(
        image: np.ndarray, n_wavelengths: int, starting_spectral_index: int) \
        -> np.ndarray:
    """Pad the spectral axis of an image with NaNs.

    The spectral axis is assumed to be the last axis, consistent with the IUVS
    standard.

    Parameters
    ----------
    image: np.ndarray
        The image to pad with NaNs. This is assumed to be 3-dimensional with
        the last axis corresponding to wavelength.
    n_wavelengths: int
        The number of wavelengths IUVS took data with.
    starting_spectral_index: int
        The starting index of the

    Returns
    -------
    np.ndarray
        The input array with NaNs padded on the ends.

    Notes
    -----
    IUVS takes data with different spectral binning schemes. Frequently, it
    doesn't have the bandwidth to transmit all the spectral data, so it only
    transmits a fraction of that data. This function puts the image in the
    place of a hypothetical array where it transmitted all data.

    This is particularly useful when fitting spectral templates to data.

    Examples
    --------
    Fit an image of shape (200, 50, 40) into a 256 spectral bin array that
    transmitted data starting at the 60th spectral bin.

    >>> import numpy as np
    >>> import pyuvs as pu
    >>> dummy_data = np.ones((200, 50, 40))
    >>> padded_data = pu.pad_spectral_image_with_nan(dummy_data, 256, 60)
    >>> padded_data.shape
    (200, 50, 256)
    >>> padded_data[0, 0, 59], padded_data[0, 0, 60]
    (nan, 1.0)

    """
    temp_array = np.full((image.shape[0], image.shape[1], n_wavelengths),
                         np.nan)
    temp_array[..., starting_spectral_index:
                    starting_spectral_index+image.shape[-1]] = image
    return temp_array


def rebin_wavelengths(
        wavelengths: np.ndarray, spectral_pixel_bin_width: int) -> np.ndarray:
    """Rebin the wavelengths to a given spectral pixel bin width.

    Parameters
    ----------
    wavelengths: np.ndarray
        The wavelengths to rebin.
    spectral_pixel_bin_width: int
        The spectral bin width.

    Returns
    -------
    np.ndarray
        Rebinned wavelengths.

    See Also
    --------
    rebin_muv_wavelengths: Identical to this function but with pre-populated
                           MUV wavelengths.

    Examples
    --------
    Rebin the MUV wavelengths to use 2 bins / spectral pixel.

    >>> import pyuvs as pu
    >>> muv_wavelengths = pu.load_muv_wavelength_centers()
    >>> rebin = pu.rebin_wavelengths(muv_wavelengths, 2)
    >>> rebin.shape
    (512,)

    """
    new_shape = (wavelengths.shape[0]//spectral_pixel_bin_width,
                 spectral_pixel_bin_width)
    return wavelengths.reshape(new_shape).mean(axis=1)


def rebin_muv_wavelengths(spectral_pixel_bin_width: int) -> np.ndarray:
    """Rebin the MUV wavelengths to a given spectral pixel bin width.

    Parameters
    ----------
    spectral_pixel_bin_width: int
        The spectral bin width.

    Returns
    -------
    np.ndarray
        Rebinned wavelengths.

    See Also
    --------
    rebin_wavelengths: This function generalized to any input wavelengths.

    Examples
    --------
    Rebin the MUV wavelengths to use 2 bins / spectral pixel.

    >>> import pyuvs as pu
    >>> rebin = pu.rebin_muv_wavelengths(2)
    >>> rebin.shape
    (512,)

    """
    return rebin_wavelengths(load_muv_wavelength_centers(),
                             spectral_pixel_bin_width)


def calculate_calibration_curve(
        detector_sensitivity_curve: np.ndarray, spatial_bin_width: int,
        wavelength_width: np.ndarray, voltage_gain: float,
        integration_time: float) -> np.ndarray:
    """Calculate the calibration curve [DN/kR].

    Parameters
    ----------
    detector_sensitivity_curve: np.ndarray
        The detector sensitivity curve.
    spatial_bin_width: int
        The spatial bin width [pixels].
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

    See Also
    --------
    calculate_muv_observational_calibration_curve: Identical to this function but
                                                 with pre-populated with the
                                                 observational MUV sensitivity
                                                 curve.

    """
    bin_omega = pixel_omega * spatial_bin_width
    return wavelength_width * voltage_gain * integration_time * kR * \
        detector_sensitivity_curve * bin_omega


def calculate_muv_observational_calibration_curve(
        spatial_bin_width: int, wavelength_width: np.ndarray,
        voltage_gain: float, integration_time: float) -> np.ndarray:
    """Calculate the calibration curve [DN/kR].

    Parameters
    ----------
    spatial_bin_width: int
        The spatial bin width [pixels].
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

    See Also
    --------
    calculate_calibration_curve: This function generalized to any calibration
                                 curve.

    """
    sensitivity = load_muv_sensitivity_curve_observational()
    return calculate_calibration_curve(
        sensitivity, spatial_bin_width, wavelength_width, voltage_gain,
        integration_time)


# TODO: document this
class MLRFitInfo:
    def __init__(self, detector_image_dark_subtracted: np.ndarray,
                 uncertainty: np.ndarray, spectral_pixel_bin_width: int,
                 starting_spectral_index: int, spatial_pixel_bin_width: int,
                 wavelength_width: float, voltage_gain: float,
                 integration_time: float):
        self.detector_image_dark_subtracted = detector_image_dark_subtracted
        self.uncertainty = uncertainty
        self.spectral_pixel_bin_width = spectral_pixel_bin_width
        self.starting_spectral_index = starting_spectral_index
        self.spatial_pixel_bin_width = spatial_pixel_bin_width
        self.wavelength_width = wavelength_width
        self.voltage_gain = voltage_gain
        self.integration_time = integration_time


    '''def fit_templates_to_nightside_data(mlr_info: MLRFitInfo) -> np.ndarray:
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


    # Load in miscellaneous info
    wavelength_center = load_muv_wavelength_centers()
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
    templates = sm.add_constant(rebinned_templates)'''

    # Pad nans
    '''We have now taken our 40 bin spectrum and placed it in its original 
    position within a 256 bin spectrum so we can fit it to the 256 bin template
    '''
    '''spectra = pad_spectral_axis_with_nan(dds, starting_spectral_index, 256)
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

    return brightnesses'''


if __name__ == '__main__':
    #from pyuvs.data_files.content import L1b
    # Get data from the files. Assume nightside settings are the same each file
    '''fc.dayside = False
    dds = fc.stack_detector_image_dark_subtracted()
    dn_unc = fc.stack_detector_image_random_uncertainty_dn()
    file = fc.get_first_nightside_file()

    spectral_pixel_bin_width = int(np.median(file.binning.spectral_pixel_bin_width))
    starting_spectral_index = int(file.binning.spectral_pixel_bin_width[0] / spectral_pixel_bin_width)
    spatial_pixel_bin_width = int(np.median(file.binning.spatial_pixel_bin_width))
    wavelength_width = np.median(file.observation.wavelength_width)
    voltage_gain = file.observation.voltage_gain
    integration_time = file.observation.integration_time'''
