from pathlib import Path
from astropy.io import fits
import numpy as np
from pyuvs.constants import day_night_voltage_boundary, minimum_mirror_angle, \
    maximum_mirror_angle


def add_integration_dimension(func):
    def wrapper(*args):
        f = func(*args)
        return f[None, :] if np.ndim(f) == 2 else f
    return wrapper


def app_flip(func):
    def wrapper(*args):
        f = func(*args)
        flip = args[0].flip
        return np.fliplr(f) if flip else f
    return wrapper


# TODO: this is incomplete
class L1bFile:
    """A data structure representing a level 1b data file.

    Parameters
    ----------
    filepath: Path
        Absolute path to the level 1b data file.

    """
    def __init__(self, filepath: Path):
        self.hdul = fits.open(filepath)

        self._primary = \
            self._get_structures('primary')
        self._random_dn_unc = \
            self._get_structures('random_dn_unc')
        # TODO: random_phy_unc
        # TODO: systematic_phy_unc
        # TODO: detector_raw
        self._detector_dark_subtracted = \
            self._get_structures('detector_dark_subtracted')
        # TODO: quality_flag
        # TODO: background_dark
        # TODO: dark_integration
        # TODO: dark_engineering
        # TODO: dark_observation
        # TODO: detector_dark
        self.integration = \
            Integration(self._get_structures('integration'))
        # TODO: engineering
        self.binning = \
            Binning(self._get_structures('binning'))
        self.spacecraft_geometry = \
            SpacecraftGeometry(self._get_structures('spacecraftgeometry'))
        self.pixel_geometry = \
            PixelGeometry(self._get_structures('pixelgeometry'))
        self.observation = \
            Observation(self._get_structures('observation'))

        self._flip = self.is_app_flipped()

        self.pixel_geometry.set_flip(self._flip)

        del self.hdul

    @property
    def flip(self):
        return self._flip

    @property
    @app_flip
    @add_integration_dimension
    def primary(self):
        return self._primary

    @property
    @app_flip
    @add_integration_dimension
    def random_uncertainty_dn(self):
        return self._random_dn_unc

    @property
    @app_flip
    @add_integration_dimension
    def detector_dark_subtracted(self):
        return self._detector_dark_subtracted

    def _get_structures(self, name: str) -> fits.fitsrec.FITS_rec:
        # or it returns np.ndarray
        return self.hdul[name].data

    def is_app_flipped(self) -> bool:
        """Determine if the APP was flipped.

        Returns
        -------
        bool
            True if the APP was flipped; False otherwise.

        """
        dot_product = np.dot(
            self.spacecraft_geometry.inertial_frame_instrument_x_unit_vector[-1],
            self.spacecraft_geometry.inertial_frame_spacecraft_velocity_vector[-1])
        return np.sign(dot_product) > 0

    def is_dayside_file(self) -> bool:
        """Determine if the input file is a file taken with dayside settings.

        Returns
        -------
        bool
            True if the file is a dayside file; False otherwise.

        """
        return self.observation.mcp_voltage < day_night_voltage_boundary

    def positive_mirror_scan_direction(self) -> bool:
        """Determine if the mirror is scanning in a positive direction.

        Returns
        -------
        True if the mirror angle is increasing each integration; False
        otherwise.

        """
        return self.integration.mirror_angle[-1] - \
            self.integration.mirror_angle[0] > 0

    def is_relay_file(self) -> bool:
        """Determine if the input file is a relay file.

        Returns
        -------
        bool
            True if the file is a relay file; False otherwise.

        """
        return np.amin(self.integration.mirror_angle) == minimum_mirror_angle \
            and np.amax(self.integration.mirror_angle) == maximum_mirror_angle


class _FitsRecord:
    def __init__(self, structure: fits.fitsrec.FITS_rec):
        self._flip = None
        self.structure = structure

    def get_substructure(self, name: str):
        return self.structure[name]

    def delete_structure(self):
        del self.structure

    def set_flip(self, flip: bool):
        self._flip = flip

    @property
    def flip(self):
        return self._flip


class Integration(_FitsRecord):
    """A data structure representing the "integration" record arrays.

    Parameters
    ----------
    structure
        The .fits record.

    """
    def __init__(self, structure: fits.fitsrec.FITS_rec):
        super().__init__(structure)

        self._timestamp = self.get_substructure('timestamp')
        self._et = self.get_substructure('et')
        self._utc = self.get_substructure('utc')
        self._mirror_dn = self.get_substructure('mirror_dn')
        self._mirror_deg = self.get_substructure('mirror_deg')
        self._fov_deg = self.get_substructure('fov_deg')
        self._lya_centroid = self.get_substructure('lya_centroid')
        self._det_temp_c = self.get_substructure('det_temp_c')
        self._case_temp_c = self.get_substructure('case_temp_c')

        self.delete_structure()

    @property
    def timestamp(self) -> np.ndarray:
        """Get the SCLK timestamp [seconds] of each integration.

        Returns
        -------
        np.ndarray
            Timestamp of each integration.

        """
        return self._timestamp

    @property
    def ephemeris_time(self) -> np.ndarray:
        """Get the ephemeris time [seconds] of each integration.

        Returns
        -------
        np.ndarray
            Ephemeris time of each integration.

        """
        return self._et

    @property
    def utc(self) -> np.ndarray:
        """Get the UTC [date string] of each integration.

        Returns
        -------
        np.ndarray
            UTC of each integration.

        """
        return self._utc

    @property
    def mirror_position(self) -> np.ndarray:
        """Get the mirror position [DN] of each integration.

        Returns
        -------
        np.ndarray
            Mirror position of each integration.

        Notes
        -----
        bscale = 1 and bzero = 32786, whatever this means.

        """
        return self._mirror_dn

    @property
    def mirror_angle(self) -> np.ndarray:
        """Get the mirror angle [degrees] of each integration.

        Returns
        -------
        np.ndarray
            Mirror angle of each integration.

        """
        return self._mirror_deg

    @property
    def field_of_view(self) -> np.ndarray:
        """Get the field of view [degrees] of each integration.

        Returns
        -------
        np.ndarray
            Field of view of each integration.

        """
        return self._fov_deg

    @property
    def lyman_alpha_centroid(self) -> np.ndarray:
        """Get the lyman-alpha centroid [pixel] of each integration.

        Returns
        -------
        np.ndarray
            Lyman-alpha centroid of each integration.

        """
        return self._lya_centroid

    @property
    def detector_temperature(self) -> np.ndarray:
        """Get the detector temperature [degrees celsius] of each integration.

        Returns
        -------
        np.ndarray
            Detector temperature of each integration.

        """
        return self._det_temp_c

    @property
    def case_temperature(self) -> np.ndarray:
        """Get the case temperature [degrees celsius] of each integration.

        Returns
        -------
        np.ndarray
            Case temperature of each integration.

        """
        return self._case_temp_c


class Binning(_FitsRecord):
    """A data structure representing the "binning" record arrays.

    Parameters
    ----------
    structure
        The .fits record.

    """
    def __init__(self, structure: fits.fitsrec.FITS_rec):
        super().__init__(structure)

        self._spabinwidth = self.get_substructure('spabinwidth')[0]
        self._spapixlo = self.get_substructure('spapixlo')[0]
        self._spebinwidth = self.get_substructure('spebinwidth')[0]
        self._spepixlo = self.get_substructure('spepixlo')[0]

        self.delete_structure()

    @property
    def spatial_pixel_bin_width(self) -> np.ndarray:
        """Get the numer of detector pixels in each spatial bin.

        Returns
        -------
        np.ndarray
            Spatial pixels in each bin.

        Notes
        -----
        This is shape (n_integrations + 2). All values except the first and
        last pixels have the same value. The 2 correspond to the large and
        small keyhole.

        """
        return self._spabinwidth

    @property
    def spatial_pixel_low(self) -> np.ndarray:
        """Get the spatial pixel where each integration starts.

        Returns
        -------
        np.ndarray
            Spatial pixels where each bin starts.

        Notes
        -----
        This is shape (n_integrations).

        """
        return self._spapixlo

    @property
    def spectral_pixel_bin_width(self) -> np.ndarray:
        """Get the numer of detector pixels in each spectral bin.

        Returns
        -------
        np.ndarray
            Spectral pixels in each bin.

        Notes
        -----
        This is shape (n_wavelengths + 2). All values except the first and
        last pixels have the same value. The 2 correspond to the large and
        small keyhole.

        """
        return self._spebinwidth

    @property
    def spectral_pixel_low(self) -> np.ndarray:
        """Get the spectral pixel where each wavelength bin starts.

        Returns
        -------
        np.ndarray
            Spectral pixels where each bin starts.

        Notes
        -----
        This is shape (n_integrations).

        """
        return self._spepixlo


# TODO: this is incomplete
class SpacecraftGeometry(_FitsRecord):
    """A data structure representing the "spacecraftgeometry" record arrays.

    Parameters
    ----------
    structure
        The .fits record.

    """
    def __init__(self, structure: fits.fitsrec.FITS_rec):
        super().__init__(structure)

        self._sub_spacecraft_lat = \
            self.get_substructure('sub_spacecraft_lat')
        self._sub_spacecraft_lon = \
            self.get_substructure('sub_spacecraft_lon')
        self._vx_instrument_inertial = \
            self.get_substructure('vx_instrument_inertial')
        self._v_spacecraft_rate_inertial = \
            self.get_substructure('v_spacecraft_rate_inertial')

        self.delete_structure()

    @property
    def sub_spacecraft_latitude(self) -> np.ndarray:
        """Get the sub-spacecraft latitude [degrees] of each integration.

        Returns
        -------
        np.ndarray
            Sub-spacecraft latitude of each integration.

        """
        return self._sub_spacecraft_lat

    @property
    def sub_spacecraft_longitude(self) -> np.ndarray:
        """Get the sub-spacecraft longitude [degrees] of each integration.

        Returns
        -------
        np.ndarray
            Sub-spacecraft longitude of each integration.

        """
        return self._sub_spacecraft_lon

    @property
    def inertial_frame_instrument_x_unit_vector(self) -> np.ndarray:
        """Get the unit vector of the "x" component of the instrument in the
        inertial frame of each integration.

        Returns
        -------
        np.ndarray
            "x" component of the instrument velocity in the inertial frame.

        """
        return self._vx_instrument_inertial

    @property
    def inertial_frame_spacecraft_velocity_vector(self) -> np.ndarray:
        """Get the spacecraft velocity vector [km/s] in the inertial frame of
        each integration.

        Returns
        -------
        np.ndarray
            Spacecraft velocity vector in the inertial frame.

        """
        return self._v_spacecraft_rate_inertial


class PixelGeometry(_FitsRecord):
    """A data structure representing the "pixelgeometry" record arrays.

    Parameters
    ----------
    structure
        The .fits record.

    Notes
    -----
    The last dimension has 5 elements. These indices are described as follows:

    0. The bottom left corner
    1. The top left corner
    2. The bottom right corner
    3. The top right corner
    4. The pixel center

    """
    def __init__(self, structure: fits.fitsrec.FITS_rec):
        super().__init__(structure)

        self._pixel_vec = \
            self.get_substructure('pixel_vec')
        self._pixel_corner_ra = \
            self.get_substructure('pixel_corner_ra')
        self._pixel_corner_dec = \
            self.get_substructure('pixel_corner_dec')
        self._pixel_corner_lat = \
            self.get_substructure('pixel_corner_lat')
        self._pixel_corner_lon = \
            self.get_substructure('pixel_corner_lon')
        self._pixel_corner_mrh_alt = \
            self.get_substructure('pixel_corner_mrh_alt')
        self._pixel_corner_mrh_alt_rate = \
            self.get_substructure('pixel_corner_mrh_alt_rate')
        self._pixel_corner_los = \
            self.get_substructure('pixel_corner_los')
        self._pixel_solar_zenith_angle = \
            self.get_substructure('pixel_solar_zenith_angle')
        self._pixel_emission_angle = \
            self.get_substructure('pixel_emission_angle')
        self._pixel_zenith_angle = \
            self.get_substructure('pixel_zenith_angle')
        self._pixel_phase_angle = \
            self.get_substructure('pixel_phase_angle')
        self._pixel_local_time = \
            self.get_substructure('pixel_local_time')

        self.delete_structure()

    @property
    @app_flip
    #@add_integration_dimension
    def vector(self) -> np.ndarray:
        """Get the unit vector of each spatial pixel corner.

        Returns
        -------
        np.ndarray
            Unit vector of each spatial pixel corner.

        Notes
        -----
        For whatever reason, this has shape in the data of
        (number of integrations, 3, number of positions, 5). I rearranged the
        axes so that this has shape
        (number of integrations, number of positions, 5, 3) so it now matches
        the same shapes as all the other arrays.

        """
        pixel_vec = self._pixel_vec
        return np.moveaxis(pixel_vec, 1, -1)

    @property
    @app_flip
    #@add_integration_dimension
    def right_ascension(self) -> np.ndarray:
        """Get the right ascension [degrees] of each spatial pixel corner.

        Returns
        -------
        np.ndarray
            Right ascension of each spatial pixel corner.

        """
        return self._pixel_corner_ra

    @property
    @app_flip
    #@add_integration_dimension
    def declination(self) -> np.ndarray:
        """Get the declination [degrees] of each spatial pixel corner.

        Returns
        -------
        np.ndarray
            Declination of each spatial pixel corner.

        """
        return self._pixel_corner_dec

    @property
    @app_flip
    #@add_integration_dimension
    def latitude(self) -> np.ndarray:
        """Get the latitude [degrees] of each spatial pixel corner.

        Returns
        -------
        np.ndarray
            Latitude of each spatial pixel corner.

        """
        return self._pixel_corner_lat

    @property
    @app_flip
    #@add_integration_dimension
    def longitude(self) -> np.ndarray:
        """Get the longitude [degrees] of each spatial pixel corner.

        Returns
        -------
        np.ndarray
            Longitude of each spatial pixel corner.

        """
        return self._pixel_corner_lon

    @property
    @app_flip
    #@add_integration_dimension
    def tangent_altitude(self) -> np.ndarray:
        """Get the altitude [km] of each spatial pixel corner.

        Returns
        -------
        np.ndarray
            Altitude of each spatial pixel corner.

        """
        return self._pixel_corner_mrh_alt

    @property
    @app_flip
    #@add_integration_dimension
    def altitude_rate(self) -> np.ndarray:
        """Get the altitude rate [km/s] of each spatial pixel corner.

        Returns
        -------
        np.ndarray
            Altitude rate of each spatial pixel corner.

        """
        return self._pixel_corner_mrh_alt_rate

    @property
    @app_flip
    #@add_integration_dimension
    def line_of_sight(self) -> np.ndarray:
        """Get the line of sight [km] of each spatial pixel corner.

        Returns
        -------
        np.ndarray
            Line of sight of each spatial pixel corner.

        """
        return self._pixel_corner_los

    @property
    @app_flip
    #@add_integration_dimension
    def solar_zenith_angle(self) -> np.ndarray:
        """Get the solar zenith angle [degrees] of each spatial pixel.

        Returns
        -------
        np.ndarray
            Solar zenith angle of each spatial pixel.

        """
        return self._pixel_solar_zenith_angle

    @property
    @app_flip
    #@add_integration_dimension
    def emission_angle(self) -> np.ndarray:
        """Get the emission angle [degrees] of each spatial pixel.

        Returns
        -------
        np.ndarray
            Emission angle of each spatial pixel.

        """
        return self._pixel_emission_angle

    @property
    @app_flip
    #@add_integration_dimension
    def zenith_angle(self) -> np.ndarray:
        """Get the zenith angle [degrees] of each spatial pixel.

        Returns
        -------
        np.ndarray
            Zenith angle of each spatial pixel.

        """
        return self._pixel_zenith_angle

    @property
    @app_flip
    #@add_integration_dimension
    def phase_angle(self) -> np.ndarray:
        """Get the phase angle [degrees] of each spatial pixel.

        Returns
        -------
        np.ndarray
            Phase angle of each spatial pixel.

        """
        return self._pixel_phase_angle

    @property
    @app_flip
    #@add_integration_dimension
    def local_time(self) -> np.ndarray:
        """Get the local time [hours] of each spatial pixel.

        Returns
        -------
        np.ndarray
            Local time of each spatial pixel.

        """
        return self._pixel_local_time


# TODO: this is incomplete
# TODO: write what MCP stands for
class Observation(_FitsRecord):
    """A data structure representing the "observation" record arrays.

    Parameters
    ----------
    structure
        The .fits record.

    """
    def __init__(self, structure: fits.fitsrec.FITS_rec):
        super().__init__(structure)

        self._int_time = \
            self.get_substructure('int_time')
        self._channel = \
            self.get_substructure('channel')
        self._mcp_volt = \
            self.get_substructure('mcp_volt')[0]
        self._mcp_gain = \
            self.get_substructure('mcp_gain')[0]
        self._wavelength = \
            self.get_substructure('wavelength')[0]
        self._wavelength_width = \
            self.get_substructure('wavelength_width')[0]

        self.delete_structure()

    @property
    def integration_time(self) -> np.float32:
        return self._int_time

    @property
    def channel(self) -> str:
        return self._channel

    @property
    def mcp_voltage(self) -> np.float32:
        """Get the MCP voltage [V] settings used to collect data in this file.

        Returns
        -------
        np.ndarray
            MCP voltage settings.

        """
        return self._mcp_volt

    @property
    def mcp_gain(self) -> np.float32:
        """Get the MCP voltage gain settings used to collect data in this file.

        Returns
        -------
        np.ndarray
            MCP voltage gain settings.

        """
        return self._mcp_gain

    @property
    def wavelength(self) -> np.ndarray:
        """Get the wavelengths used throughout this file.

        Returns
        -------
        np.ndarray
            The wavelengths.

        Notes
        -----
        All integrations have the same wavelengths, so this shape is
        (n_spatial_bins, n_spectral_bins).

        """
        return self._wavelength

    @property
    def wavelength_width(self) -> np.ndarray:
        """Get the width of the wavelengths used throughout this file.

        Returns
        -------
        np.ndarray
            The wavelength widths.

        Notes
        -----
        All integrations have the same wavelengths, so this shape is
        (n_spatial_bins, n_spectral_bins).

        """
        return self._wavelength_width


def add_additional_axis(array: np.ndarray) -> np.ndarray:
    return array[None, :]


def cast_array_to_3d(array: np.ndarray) -> np.ndarray:
    return add_additional_axis(array) if np.ndim(array) == 2 else array


def stack_daynight_primary(files: list[L1bFile], dayside: bool = True):
    return np.vstack([f.primary for f in files if f.is_dayside_file() == dayside])


def stack_daynight_solar_zenith_angle(files: list[L1bFile], dayside: bool = True):
    return np.vstack([f.pixel_geometry.solar_zenith_angle for f in files
                      if f.is_dayside_file() == dayside])


def stack_daynight_emission_angle(files: list[L1bFile], dayside: bool = True):
    return np.vstack([f.pixel_geometry.emission_angle for f in files
                      if f.is_dayside_file() == dayside])


def stack_daynight_phase_angle(files: list[L1bFile], dayside: bool = True):
    return np.vstack([f.pixel_geometry.phase_angle for f in files
                      if f.is_dayside_file() == dayside])


def stack_daynight_local_time(files: list[L1bFile], dayside: bool = True):
    return np.vstack([f.pixel_geometry.local_time for f in files
                      if f.is_dayside_file() == dayside])


def stack_mirror_angles(files: list[L1bFile]):
    return np.concatenate([f.integration.mirror_angle for f in files])


def stack_daynight_altitude_center(files: list[L1bFile], dayside: bool = True):
    return np.vstack([f.pixel_geometry.tangent_altitude[..., 4] for f in files if f.is_dayside_file() == dayside])


def make_daynight_on_disk_mask(files: list[L1bFile], dayside: bool = True):
    altitudes = stack_daynight_altitude_center(files, dayside=dayside)
    return np.where(altitudes == 0, True, False)


def make_dayside_integration_mask(files: list[L1bFile]):
    return np.concatenate([np.repeat(f.is_dayside_file(), f.primary.shape[0]) for f in files])


def set_off_disk_pixels_to_nan(array: np.ndarray, on_disk_mask: np.ndarray):
    return np.where(on_disk_mask, array, np.nan)


if __name__ == '__main__':
    from pyuvs.data_files.path import find_latest_apoapse_muv_file_paths_from_block
    p = Path('/media/kyle/Samsung_T5/IUVS_Data')
    files = find_latest_apoapse_muv_file_paths_from_block(p, 3453)
    hdul = fits.open(files[0])
