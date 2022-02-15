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


def fit_muv_templates_to_nightside_data(
        detector_image_dark_subtracted: np.ndarray,
        uncertainty: np.ndarray, wavelength_width: np.ndarray,
        pixels_per_spatial_bin: int, pixels_per_spectral_bin: int,
        starting_spectral_index: int, voltage_gain: float,
        integration_time: float) -> np.ndarray:
    """Use multiple linear regression (MLR) to fit templates to nightside data.

    Parameters
    ----------
    detector_image_dark_subtracted: np.ndarray
        The detector image with dark current subtracted. This array is assumed
        to be 3-dimensional.
    uncertainty: np.ndarray
        The uncertainty associated with :code:`detector_image_dark_subtracted`.
        This array is assumed to have the same shape as
        :code:`detector_image_dark_subtracted`.
    wavelength_width: np.ndarray
        The wavelength width. This array is assumed to be 1-dimensional and
        have the same shape as the last axis of
        :code:`detector_image_dark_subtracted`.
    pixels_per_spatial_bin: int
        The number of detector pixels in each spatial bin.
    pixels_per_spectral_bin: int
        The number of detector pixels in each spectral bin.
    starting_spectral_index: int
        The starting spectral index.
    voltage_gain: float
        The voltage gain settings.
    integration_time: float
        The integration time.

    Returns
    -------
    np.ndarray
        The fitted brightnesses of the spectral components. This array has
        shape (3, n_integrations, n_positions). Along the first axis, index 0
        corresponds to NO nightglow, index 1 corresponds to aurora, and index
        2 corresponds to solar continuum.

    Notes
    -----
    This fits 4 nightside templates to IUVS data: NO nightglow, CO Cameron
    bands, the ultraviolet doublet (UVD), and solar continuum. The CO Cameron
    bands and UVD collectively make an aurora template.

    This function also uses the MUV wavelengths and MUV sensitivity curve that
    comes with pyuvs.

    """
    # Compute some detector curves
    rebinned_wavelengths = rebin_muv_wavelengths(pixels_per_spectral_bin)
    rebinned_sensitivity_curve = np.interp(
        rebinned_wavelengths,
        load_muv_sensitivity_curve_observational()[:, 0],
        load_muv_sensitivity_curve_observational()[:, 1])
    rebinned_calibration_curve = calculate_calibration_curve(
        rebinned_sensitivity_curve,
        pixels_per_spatial_bin, wavelength_width,
        voltage_gain, integration_time)

    # Rebin the templates
    fit_templates = load_standard_fit_templates()
    rebinned_templates = rebin_templates(fit_templates, pixels_per_spectral_bin).T
    templates = sm.add_constant(rebinned_templates)

    # Pad nans
    spectral_scheme = 1024 // pixels_per_spectral_bin
    spectra = pad_spectral_image_with_nan(
        detector_image_dark_subtracted, spectral_scheme, starting_spectral_index)
    uncertainty = pad_spectral_image_with_nan(
        uncertainty, spectral_scheme, starting_spectral_index)

    # Fit templates to the data
    brightnesses = np.zeros((3,) + detector_image_dark_subtracted.shape[:-1])
    for f in range(brightnesses.shape[1]):
        for g in range(brightnesses.shape[2]):
            fit = sm.WLS(spectra[f, g, :], templates,
                         weights=1 / uncertainty[f, g, :] ** 2,
                         missing='drop').fit()  # This ignores NaNs
            coeff = fit.params
            no_brightness = np.sum(coeff[1] * templates[:, 1] * wavelength_width / rebinned_calibration_curve)
            aurora_brightness = np.sum(coeff[2] * templates[:, 2] * wavelength_width  / rebinned_calibration_curve) + \
                                np.sum(coeff[3] * templates[:, 3] * wavelength_width / rebinned_calibration_curve)
            solar_brightness = np.sum(coeff[4] * templates[:, 4] * wavelength_width  / rebinned_calibration_curve)

            if f == 150 and g == 5:
                fig, ax = plt.subplots()
                ax.plot(wavs, dds[f, g])
                ax.plot(rebinned_wavelengths, coeff[0] + rebinned_templates[:, 0] * coeff[1] +
                        rebinned_templates[:, 1] * coeff[2] + rebinned_templates[:, 2] * coeff[3] +
                        rebinned_templates[:, 3] * coeff[4])
                plt.savefig('/home/kyle/ql_testing/spectrafit.png')
            brightnesses[0, f, g] = no_brightness
            brightnesses[1, f, g] = aurora_brightness
            brightnesses[2, f, g] = solar_brightness

    return brightnesses


if __name__ == '__main__':
    from pathlib import Path
    import matplotlib.colors as colors
    import matplotlib.pyplot as plt
    from pyuvs.data_files.contents import L1bFileCollection, L1bFile
    from pyuvs.data_files.path import find_latest_apoapse_muv_file_paths_from_block
    #p = Path('/media/kyle/T7/IUVS_data')
    #files = find_latest_apoapse_muv_file_paths_from_block(p, 13000)
    p = Path('/media/kyle/T7/IUVS_data')
    o = 13000
    files = find_latest_apoapse_muv_file_paths_from_block(p, o)

    fc = L1bFileCollection([L1bFile(f) for f in files])

    wavs = L1bFile(files[0]).observation.wavelength[0, :]
    # Get data from the files. Assume nightside settings are the same each file
    fc.dayside = False
    dds = fc.stack_detector_image_dark_subtracted()
    dn_unc = fc.stack_detector_image_random_uncertainty_dn()
    file = fc.get_first_nightside_file()

    spbw = int(np.median(file.binning.spectral_pixel_bin_width))
    print(spbw)
    ssi = int(file.binning.spectral_pixel_bin_width[0] / spbw)
    spapbw = int(np.median(file.binning.spatial_pixel_bin_width))
    ww = np.median(file.observation.wavelength_width)
    vg = file.observation.voltage_gain
    it = file.observation.integration_time

    kray = fit_muv_templates_to_nightside_data(dds, dn_unc, ww, spapbw, spbw, ssi, vg, it)

    fig, ax = plt.subplots(1, 3)
    #n = colors.SymLogNorm(linthresh=1, vmin=0, vmax=10)
    # NO: LogNorm from 0.5 to 4
    # Aurora: LogNorm from 0.1 to 1
    noo = colors.LogNorm()
    n = colors.LogNorm()
    ax[0].imshow(kray[0, ...], cmap='viridis', norm=noo)
    ax[1].imshow(kray[1, ...], cmap='magma', norm=n)
    ax[2].imshow(kray[2, ...], cmap='viridis', norm=n)
    plt.savefig(f'/home/kyle/ql_testing/mlr{o}.png', dpi=150)
