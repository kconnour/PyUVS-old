"""This module provides functions to load in standard dictionaries and arrays
for working with IUVS data."""
from pathlib import Path
import numpy as np


def _get_package_path() -> Path:
    return Path(__file__).parent.resolve()


def _get_anc_directory() -> Path:
    return _get_package_path() / 'anc'


def _get_flatfield_directory() -> Path:
    return _get_anc_directory() / 'flatfields'


def _get_instrument_directory() -> Path:
    return _get_anc_directory() / 'instrument'


def _get_maps_directory() -> Path:
    return _get_anc_directory() / 'maps'


def _get_templates_directory() -> Path:
    return _get_anc_directory() / 'templates'


# Flatfields
# TODO: fix the tight layout in the graphics of documentation
def load_flatfield_mid_hi_res_pipeline() -> np.ndarray:
    """Load mid-hi-resolution flatfield used in the pipeline.

    This array has a shape of (133, 19).

    Returns
    -------
    np.ndarray
        Array of the flatfield.

    Notes
    -----
    This flatfield was made from orbits XXXX to YYYY.

    Examples
    --------
    Visualize this flatfield.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       flatfield = pu.load_flatfield_mid_hi_res_pipeline()
       ax.imshow(flatfield.T, cmap='inferno')
       ax.set_xlabel('Spatial bin')
       ax.set_ylabel('Spectral bin')
       plt.show()

    """
    return np.load(str(_get_flatfield_directory() /
                   'mid-hi-res-flatfield-pipeline.npy'))


# TODO: fix the tight layout in the graphics of documentation
def load_flatfield_mid_hi_res_my34gds() -> np.ndarray:
    """Load mid-hi-resolution flatfield created from data taken during the
    Mars year 34 global dust storm.

    This array has a shape of (133, 19).

    Returns
    -------
    np.ndarray
        Array of the flatfield.

    Notes
    -----
    This flatfield was made from orbits XXXX to YYYY.

    Examples
    --------
    Visualize this flatfield.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       flatfield = pu.load_flatfield_mid_hi_res_my34gds()
       ax.imshow(flatfield.T, cmap='inferno')
       ax.set_xlabel('Spatial bin')
       ax.set_ylabel('Spectral bin')
       plt.show()

    """
    return np.load(str(_get_flatfield_directory() /
                   'mid-hi-res-flatfield-my34gds.npy'))


# TODO: fix the tight layout in the graphics of documentation
def load_flatfield_hi_res() -> np.ndarray:
    """Load hi-resolution flatfield created from data taken during outdisk.

    This array has a shape of (200, 19).

    Returns
    -------
    np.ndarray
        Array of the flatfield.

    Notes
    -----
    This flatfield was made from orbits XXXX to YYYY.

    Examples
    --------
    Visualize this flatfield.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       flatfield = pu.load_flatfield_hi_res()
       ax.imshow(flatfield.T, cmap='inferno')
       ax.set_xlabel('Spatial bin')
       ax.set_ylabel('Spectral bin')
       plt.show()

    """
    return np.load(str(_get_flatfield_directory() /
                   'hi-res-flatfield.npy'))


# TODO: fix the tight layout in the graphics of documentation
def load_flatfield_mid_res_app_flip() -> np.ndarray:
    """Load mid-resolution flatfield created from data taken when the APP was
    flipped.

    This array has a shape of (50, 19).

    Returns
    -------
    np.ndarray
        Array of the flatfield.

    Notes
    -----
    This flatfield was made from orbits 3744 to 3750.

    Examples
    --------
    Visualize this flatfield.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       flatfield = pu.load_flatfield_mid_res_app_flip()
       ax.imshow(flatfield.T, cmap='inferno')
       ax.set_xlabel('Spatial bin')
       ax.set_ylabel('Spectral bin')
       plt.show()

    """
    return np.load(str(_get_flatfield_directory() /
                   'mid-res-flatfield-APP-flip.npy'))


# TODO: fix the tight layout in the graphics of documentation
def load_flatfield_mid_res_no_app_flip() -> np.ndarray:
    """Load mid-resolution flatfield created from data taken when the APP was
    not flipped.

    This array has a shape of (50, 19).

    Returns
    -------
    np.ndarray
        Array of the flatfield.

    Notes
    -----
    This flatfield was made from orbits 3733 to 3739.

    Examples
    --------
    Visualize this flatfield.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       flatfield = pu.load_flatfield_mid_res_no_app_flip()
       ax.imshow(flatfield.T, cmap='inferno')
       ax.set_xlabel('Spatial bin')
       ax.set_ylabel('Spectral bin')
       plt.show()

    """
    return np.load(str(_get_flatfield_directory() /
                   'mid-res-flatfield-no-APP-flip.npy'))


# Instrument
def load_fuv_sensitivity_curve_manufacturer() -> np.ndarray:
    """Load the FUV factory sensitivity curve as reported by manufacturer.

    This array has a shape of (101, 2). Index 0 of the first axis is the
    wavelength corresponding to the sensitivity curve; index 1 is the
    sensitivity curve.

    Returns
    -------
    np.ndarray
        Array of the FUV sensitivity curve.

    Notes
    -----
    This is the detector sensitivity in DN / (photons / cm :sup:`2`) at
    gain = 1. The manufacturer reported this curve June 9, 2014.

    Examples
    --------
    Plot the sensitivity curve.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import numpy as np
       import pyuvs as pu

       fig, ax = plt.subplots()

       curve = pu.load_fuv_sensitivity_curve_manufacturer()
       ax.plot(curve[:, 0], curve[:, 1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Detector Sensitivity')
       ax.set_xlim(100, 200)
       ax.set_ylim(0, 0.1)
       plt.show()

    """
    return np.load(str(_get_instrument_directory() /
                       'fuv_sensitivity_curve_manufacturer.npy'))


def load_muv_point_spread_function() -> np.ndarray:
    """Load the MUV point spread function.

    This array has a shape of (181,).

    Returns
    -------
    np.ndarray
        Array of the point spread function.

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import numpy as np
       import pyuvs as pu

       fig, ax = plt.subplots()

       psf = pu.load_muv_point_spread_function()
       angles = np.linspace(0, 180, num=181)
       ax.plot(angles, psf)
       ax.set_xlabel('Angle [degrees]')
       ax.set_ylabel('Point spread function')
       plt.show()

    """
    return np.load(str(_get_instrument_directory() /
                       'muv_point_spread_function.npy'))


def load_muv_sensitivity_curve_manufacturer() -> np.ndarray:
    """Load the MUV factory sensitivity curve as reported by manufacturer.

    This array has a shape of (101, 2). Index 0 of the first axis is the
    wavelength corresponding to the sensitivity curve; index 1 is the
    sensitivity curve.

    Returns
    -------
    np.ndarray
        Array of the MUV sensitivity curve.

    Notes
    -----
    This is the detector sensitivity in DN / (photons / cm :sup:`2`) at
    gain = 1. The manufacturer reported this curve June 9, 2014.

    See Also
    --------
    load_muv_sensitivity_curve_observational: This curve created from
                                              observational data.

    Examples
    --------
    Plot the sensitivity curve.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import numpy as np
       import pyuvs as pu

       fig, ax = plt.subplots()

       curve = pu.load_muv_sensitivity_curve_manufacturer()
       ax.plot(curve[:, 0], curve[:, 1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Detector Sensitivity')
       ax.set_xlim(170, 360)
       ax.set_ylim(0, 0.06)
       plt.show()

    """
    return np.load(str(_get_instrument_directory() /
                       'muv_sensitivity_curve_manufacturer.npy'))


def load_muv_sensitivity_curve_observational() -> np.ndarray:
    """Load the MUV factory sensitivity curve derived from observations.

    This array has a shape of (512, 2). Index 0 of the first axis is the
    wavelength corresponding to the sensitivity curve; index 1 is the
    sensitivity curve.

    Returns
    -------
    np.ndarray
        Array of the MUV sensitivity curve.

    Notes
    -----
    This is the detector sensitivity in DN / (photons / cm :sup:`2`) at
    gain = 1. Justin Deighan reported this curve October 19, 2018.

    See Also
    --------
    load_muv_sensitivity_curve_manufacturer: This curve reported by the
                                             manufacturer.

    Examples
    --------
    Plot the sensitivity curve.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import numpy as np
       import pyuvs as pu

       fig, ax = plt.subplots()

       curve = pu.load_muv_sensitivity_curve_observational()
       ax.plot(curve[:, 0], curve[:, 1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Detector Sensitivity')
       ax.set_xlim(170, 360)
       ax.set_ylim(0, 0.06)
       plt.show()

    """
    return np.load(str(_get_instrument_directory() /
                       'muv_sensitivity_curve_observational.npy'))


def load_muv_wavelength_edge() -> np.ndarray:
    """Load the MUV wavelength edge.

    This array has a shape of (1025,).

    Returns
    -------
    np.ndarray
        Array of the edge MUV wavelengths.

    """
    return np.load(str(_get_instrument_directory() /
                       'muv_wavelength_edges.npy'))


def load_muv_wavelength_center() -> np.ndarray:
    """Load the MUV wavelength center.

    This array has a shape of (1024,).

    Returns
    -------
    np.ndarray
        Array of the center MUV wavelengths.

    """
    return np.load(str(_get_instrument_directory() /
                       'muv_wavelength_centers.npy'))


# Maps
# TODO: fix the tight layout in the graphics of documentation
def load_map_magnetic_field_closed_probability() -> np.ndarray:
    """Load the map denoting the probability of a closed magnetic field line.

    This array has a shape of (180, 360).

    Returns
    -------
    np.ndarray
        Array of the image.

    Notes
    -----
    This map comes from MGS data.

    * The 0 :sup:`th` axis corresponds to latitude and spans -90 to 90 degrees.
    * The 1 :sup:`st` axis corresponds to east longitude and spans 0 to 360
      degrees.

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       b_field = pu.anc.load_map_magnetic_field_closed_probability()
       ax.imshow(b_field, cmap='Blues_r', origin='lower')
       plt.show()

    """
    file_path = _get_maps_directory() / \
        'magnetic_field_closed_probability.npy'
    return np.load(str(file_path))


# TODO: fix the tight layout in the graphics of documentation
def load_map_magnetic_field_open_probability() -> np.ndarray:
    """Load the map denoting the probability of an open magnetic field line.

    This array has a shape of (180, 360).

    Returns
    -------
    np.ndarray
        Array of the image.

    Notes
    -----
    This map comes from MGS data.

    * The 0 :sup:`th` axis corresponds to latitude and spans -90 to 90 degrees.
    * The 1 :sup:`st` axis corresponds to east longitude and spans 0 to 360
      degrees.

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       b_field = pu.anc.load_map_magnetic_field_open_probability()
       ax.imshow(b_field, cmap='Blues_r', origin='lower')
       plt.show()

    """
    file_path = _get_maps_directory() / \
        'magnetic_field_open_probability.npy'
    return np.load(str(file_path))


# TODO: fix the tight layout in the graphics of documentation
def load_map_mars_surface() -> np.ndarray:
    """Load the Mars surface map.

    The shape of this array is (1800, 3600, 4).

    Returns
    -------
    np.ndarray
        Array of the image.

    Notes
    -----

    * The 0 :sup:`th` axis corresponds to latitude and spans 90 to -90 degrees.
    * The 1 :sup:`st` axis corresponds to east longitude and spans 0 to 360
      degrees.
    * The 2 :sup:`nd` axis is the RGBA channel.

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       surface_map = pu.anc.load_map_mars_surface()
       ax.imshow(surface_map)
       plt.show()

    """
    file_path = _get_maps_directory() / 'mars_surface.npy'
    return np.load(str(file_path))


# Templates
def load_template_co_cameron_bands() -> np.ndarray:
    """Load the MUV CO Cameron band template.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.anc.load_template_co_cameron_bands()
       wavelengths = pu.anc.load_muv_wavelength_center()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')
       plt.show()

    """
    return np.load(str(_get_templates_directory() / 'co_cameron_bands.npy'))


def load_template_co_plus_1st_negative() -> np.ndarray:
    """Load the MUV CO :sup:`+` 1NG (first negative) template.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.anc.load_template_co_plus_1st_negative()
       wavelengths = pu.anc.load_muv_wavelength_center()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')
       plt.show()

    """
    return np.load(str(_get_templates_directory() / 'co+_first_negative.npy'))


def load_template_co2_plus_fdb() -> np.ndarray:
    """Load the MUV CO :sub:`2` :sup:`+` FDB (Fox-Duffendack-Barker) template.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.anc.load_template_co2_plus_fdb()
       wavelengths = pu.anc.load_muv_wavelength_center()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')
       plt.show()

    """
    return np.load(str(_get_templates_directory() /
                       'co2+_fox_duffendack_barker.npy'))


def load_template_co2_plus_uvd() -> np.ndarray:
    """Load the MUV CO :sub:`2` :sup:`+` UVD (ultraviolet doublet) template.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.anc.load_template_co2_plus_uvd()
       wavelengths = pu.anc.load_muv_wavelength_center()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')
       plt.show()

    """
    return np.load(str(_get_templates_directory() /
                       'co2+_ultraviolet_doublet.npy'))


def load_template_n2_vk() -> np.ndarray:
    """Load the MUV N :sub:`2` VK (Vegard-Kaplan) template.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.anc.load_template_n2_vk()
       wavelengths = pu.anc.load_muv_wavelength_center()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')
       plt.show()

    """
    return np.load(str(_get_templates_directory() /
                       'nitrogen_vegard_kaplan.npy'))


def load_template_no_nightglow() -> np.ndarray:
    """Load the MUV NO nightglow template.

    This array has a shape of (1024,).

    Returns
    -------
    np.ndarray
        Array of the template.

    Examples
    --------
    Plot a composite template of all templates in detector space.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.anc.load_template_no_nightglow()
       wavelengths = pu.anc.load_muv_wavelength_center()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')
       plt.show()

    """
    return np.load(str(_get_templates_directory() / 'no_nightglow.npy'))


def load_template_oxygen_2972() -> np.ndarray:
    """Load the MUV oxygen 297.2 nm template.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.anc.load_template_oxygen_2972()
       wavelengths = pu.anc.load_muv_wavelength_center()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')
       plt.show()

    """
    return np.load(str(_get_templates_directory() / 'oxygen_2972.npy'))


def load_template_solar_continuum() -> np.ndarray:
    """Load the MUV solar continuum template.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.anc.load_template_solar_continuum()
       wavelengths = pu.anc.load_muv_wavelength_center()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')
       plt.show()

    """
    return np.load(str(_get_templates_directory() / 'solar_continuum.npy'))
