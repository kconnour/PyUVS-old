"""This module provides classes and functions for manipulating data files.
"""
from functools import wraps
from pathlib import Path
from astropy.io import fits
import numpy as np
from pyuvs.constants import minimum_mirror_angle, maximum_mirror_angle, \
    day_night_voltage_boundary


# TODO: this should go in L1bFile since it only applies there
def add_integration_dimension(func):
    @wraps(func)
    def wrapper(*args):
        f = func(*args)
        return f[None, :] if np.ndim(f) == 2 else f
    return wrapper


# TODO: this should go in L1bFile since it only applies there
def app_flip(func):
    @wraps(func)
    def wrapper(*args):
        f = func(*args)
        flip = args[0].flip
        return np.fliplr(f) if flip else f
    return wrapper


class L1bFile:
    """A data structure representing a level 1b data file.

    This class accepts an l1b data file and reads in all of its info into
    a nested data structure that roughly mimics the structure of the l1b file.
    It adds an integration dimension when that dimension is missing from the
    original data and also flips the data over the spatial dimensions if the
    APP is flipped.

    .. warning::
       Many of these structures are incomplete

    Parameters
    ----------
    filepath: Path
        Absolute path to the level 1b data file.

    """
    def __init__(self, filepath: Path):
        self.hdul = fits.open(filepath)
        self._detector_image = \
            self.DetectorImage(self.hdul)
        self._integration = \
            self.Integration(self.hdul['integration'])
        # TODO: Engineering
        self._binning = \
            self.Binning(self.hdul['binning'])
        self._spacecraft_geometry = \
            self.SpacecraftGeometry(self.hdul['spacecraftgeometry'])
        self._pixel_geometry = \
            self.PixelGeometry(self.hdul['pixelgeometry'])
        self._observation = \
            self.Observation(self.hdul['observation'])
        self._dark_integration = \
            self.Integration(self.hdul['dark_integration'])
        # TODO: DarkEngineering
        self._dark_observation = \
            self.Observation(self.hdul['dark_observation'])

        self._flip = self.is_app_flipped()
        self._detector_image.set_flip(self.flip)
        self._pixel_geometry.set_flip(self.flip)

        del self.hdul

    class _FitsRecord:
        def __init__(self):
            self._flip = None

        def set_flip(self, flip: bool):
            self._flip = flip

        @property
        def flip(self):
            return self._flip

    class DetectorImage(_FitsRecord):
        """Get the arrays of the detector image.

        All the arrays have shape (number of integrations, number of spatial
        pixels, number of spectral pixels) except detector_dark.

        Parameters
        ----------
        hdul: fits.hdu.hdulist.HDUList
            The l1b hdulist.

        """
        def __init__(self, hdul: fits.hdu.hdulist.HDUList):
            super().__init__()
            self._primary = hdul['primary']
            self._random_dn_unc = hdul['random_dn_unc']
            self._random_phy_unc = hdul['random_phy_unc']
            self._systematic_phy_unc = hdul['systematic_phy_unc']
            self._detector_raw = hdul['detector_raw']
            self._detector_dark_subtracted = hdul['detector_dark_subtracted']
            self._quality_flag = hdul['quality_flag']
            self._background_dark = hdul['background_dark']
            self._detector_dark = hdul['detector_dark']

        @property
        @app_flip
        @add_integration_dimension
        def raw(self) -> np.ndarray:
            """Get the detector image without any corrections [DN].

            Returns
            -------
            np.ndarray
                The raw detector image.

            """
            return self._detector_raw.data

        @property
        @app_flip
        @add_integration_dimension
        def random_uncertainty_dn(self) -> np.ndarray:
            """Get the random uncertainty [DN] of the detector image.

            This is the uncertainty corresponding to :py:attr:`~raw`.

            Returns
            -------
            np.ndarray
                The random uncertainty of the detector image [DN].

            """

            return self._random_dn_unc.data

        @property
        @app_flip
        @add_integration_dimension
        def dark_current(self) -> np.ndarray:
            """Get the dark current in detector image [DN].

            Returns
            -------
            np.ndarray
                The dark current in the detector image [DN].

            """

            return self._background_dark

        @property
        @app_flip
        @add_integration_dimension
        def dark_subtracted(self) -> np.ndarray:
            """Get the detector image with dark current subtracted [DN].

            Returns
            -------
            np.ndarray
                The dark-current-corrected detector image [DN].

            Notes
            -----
            This array is simply :py:attr:`~raw` - :py:attr:`~dark_current`.

            """

            return self._detector_dark_subtracted

        @property
        @app_flip
        @add_integration_dimension
        def calibrated(self) -> np.ndarray:
            """Get the calibrated detector image [kR/nm].

            Returns
            -------
            np.ndarray
                The calibrated detector image.

            Notes
            -----
            This array divided by :py:attr:`~dark_subtracted` gives arrays of
            the calibration curves.

            """
            return self._primary.data

        @property
        @app_flip
        @add_integration_dimension
        def random_uncertainty_physical(self) -> np.ndarray:
            """Get the random uncertainty [kR/nm] of the detector image.

            Returns
            -------
            np.ndarray
                The random uncertainty of the detector image [kR/nm].
            """

            return self._random_phy_unc.data

        @property
        @app_flip
        @add_integration_dimension
        def total_uncertainty_physical(self) -> np.ndarray:
            """Get the combined random and systematic uncertainty [kR/nm] of
            the detector image.

            Returns
            -------
            np.ndarray
                The total uncertainty of the detector image [kR/nm].
            """

            return self._systematic_phy_unc.data

        @property
        @app_flip
        @add_integration_dimension
        def detector_dark(self) -> np.ndarray:
            """Get the detector dark

            Returns
            -------
            np.ndarray
                The detector dark [DN].
            """

            return self._detector_dark.data

        @property
        @app_flip
        @add_integration_dimension
        def quality_flag(self) -> np.ndarray:
            """Get the quality flag.

            Returns
            -------
            np.ndarray
                The quality flag.

            """

            return self._quality_flag

        @property
        def disclaimer(self) -> str:
            """Get the disclaimer associated with this data product.

            Returns
            -------
            str
                The disclaimer.

            """
            return self._primary.header['comment']

        @property
        def filename(self) -> str:
            """Get the filename.

            Returns
            -------
            str
                The filename of this data file.

            """
            return self._primary.header['filename']

        @property
        def capture_time(self) -> str:
            """Get the capture (ephemeris) time of the start of this file.

            Returns
            -------
            str
                The capture time.

            """
            return self._primary.header['capture']

        @property
        def processing_time(self) -> str:
            """Get the processing time of this file.

            Returns
            -------
            str
                The processing time.

            """
            return self._primary.header['process']

        @property
        def channel(self) -> str:
            """Get the spectral channel of this file.

            Returns
            -------
            str
                The spectral channel.

            """
            return self._primary.header['xuv']

        @property
        def observation_id(self) -> int:
            """Get the observation ID.

            This is presumably the downlink bundle number.

            Returns
            -------
            int
                The observation ID.

            """
            return self._primary.header['obs_id']

        @property
        def number_absent_bins(self) -> int:
            """Get the number of absent bins in the observation.

            Returns
            -------
            int
                The number of absent bins.

            """
            return self._primary.header['n_fill']

        @property
        def spatial_bin_offset(self) -> int:
            """Get the starting spatial bin in this set of measurements.

            Returns
            -------
            int
                The starting spatial bin.

            """
            return self._primary.header['spa_ofs']

        @property
        def spectral_bin_offset(self) -> int:
            """Get the starting spectral bin in this set of measurements.

            Returns
            -------
            int
                The starting spectral bin.

            """
            return self._primary.header['spe_ofs']

        @property
        def spatial_bin_size(self) -> int:
            """Get the number of spatial detector pixels in each spatial bin.

            Returns
            -------
            int
                The size of a spatial bin.

            """
            return self._primary.header['spa_size']

        @property
        def spectral_bin_size(self) -> int:
            """Get the number of spectral detector pixels in each spectral bin.

            Returns
            -------
            int
                The size of a spectral bin.

            """
            return self._primary.header['spe_size']

    class Integration:
        """Get the arrays of the integrations.

        Parameters
        ----------
        integration
            The integration structure.

        """
        def __init__(self, integration):
            self._integration = integration.data

        @property
        def timestamp(self) -> np.ndarray:
            """Get the time that each integration began [SCLK seconds].

            These are in the spacecraft clock (SCLK) seconds.

            Returns
            -------
            np.ndarray
                The timestamp of each integration.

            """
            return self._integration['timestamp']

        @property
        def ephemeris_time(self) -> np.ndarray:
            """Get the time that each integration began [ephemeris seconds].

            This is the time corrected for spacecraft clock errors.

            Returns
            -------
            np.ndarray
                The ephemeris time of each integration.

            """
            return self._integration['et']

        @property
        def utc(self) -> np.ndarray:
            """Get the UTC time that each integration began [date string].

            This is the time corrected for spacecraft clock errors.

            Returns
            -------
            np.ndarray
                The UTC time of each integration.

            """
            return self._integration['utc']

        @property
        def mirror_angle_dn(self) -> np.ndarray:
            """Get the mirror angle of the integration [DN].

            Returns
            -------
            np.ndarray
                The mirror angle of each integration.

            """
            return self._integration['mirror_dn']

        @property
        def mirror_angle_degree(self) -> np.ndarray:
            """Get the mirror angle of the integration [degrees].

            Returns
            -------
            np.ndarray
                The mirror angle of each integration.

            """
            return self._integration['mirror_deg']

        @property
        def field_of_view(self) -> np.ndarray:
            """Get the instrument center field of view of each integration
            [degrees].

            Returns
            -------
            np.ndarray
                The field of view of each integration.

            Notes
            -----
            This array is simply :py:attr:`~mirror_angle_degree` * 2.

            """
            return self._integration['fov_deg']

        @property
        def pixel_shift(self) -> np.ndarray:
            """Get the pixel shift of the wavelengths computed from the
            Lyman-alpha centroid [pixels] of each integration.

            Returns
            -------
            np.ndarray
                The wavelength pixel shift.

            """
            return self._integration['lya_centroid']

        @property
        def detector_temperature(self) -> np.ndarray:
            """Get the detector temperature [degrees celsius] of each
            integration.

            Returns
            -------
            np.ndarray
                The detector temperature of each integration.

            """
            return self._integration['det_temp_c']

        @property
        def case_temperature(self) -> np.ndarray:
            """Get the instrument's case temperature [degrees celsius] of each
            integration.

            Returns
            -------
            np.ndarray
                The instrument case temperature of each integration.

            """
            return self._integration['case_temp_c']

    class Binning:
        """Get the arrays of the binning.

        Parameters
        ----------
        binning
            The binning structure.

        """

        def __init__(self, binning):
            self._binning = binning.data

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
            return self._binning['spabinwidth']

        @property
        def spatial_pixel_low(self) -> np.ndarray:
            """Get the spatial pixel where each spatial bin starts.

            Returns
            -------
            np.ndarray
                Spatial pixels where each bin starts.

            Notes
            -----
            This is shape (n_integrations).

            """
            return self._binning['spapixlo']

        @property
        def spatial_pixel_high(self) -> np.ndarray:
            """Get the spatial pixel where each spatial bin ends.

            Returns
            -------
            np.ndarray
                Spatial pixels where each bin eds.

            Notes
            -----
            This is shape (n_integrations).

            """
            return self._binning['spapixhi']

        @property
        def spatial_pixel_transmit(self) -> np.ndarray:
            """Get whether the spatial pixels were transmitted.

            Returns
            -------
            np.ndarray
                Spatial pixel transmission.

            """
            return self._binning['spabintransmit']

        @property
        def spatial_bin_size(self) -> int:
            """Get the spatial pixel bin size.

            Returns
            -------
            int
                Spatial pixel bin size.

            """
            return int(np.median(self.spatial_pixel_bin_width))

        @property
        def spatial_bin_offset(self) -> int:
            """Get the spatial pixel bin offset.

            Returns
            -------
            int
                Spatial pixel bin offset.

            """
            return self.spatial_pixel_low[0, 0]

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
            return self._binning['spebinwidth']

        @property
        def spectral_pixel_low(self) -> np.ndarray:
            """Get the spectral pixel where each spectral bin starts.

            Returns
            -------
            np.ndarray
                Spectral pixels where each bin starts.

            Notes
            -----
            This is shape (n_integrations).

            """
            return self._binning['spepixlo']

        @property
        def spectral_pixel_high(self) -> np.ndarray:
            """Get the spatial pixel where each spectral bin ends.

            Returns
            -------
            np.ndarray
                Spatial pixels where each bin eds.

            Notes
            -----
            This is shape (n_integrations).

            """
            return self._binning['spepixhi']

        @property
        def spectral_pixel_transmit(self) -> np.ndarray:
            """Get whether the spectral pixels were transmitted.

            Returns
            -------
            np.ndarray
                Spectral pixel transmission.

            """
            return self._binning['spebintransmit']

        @property
        def spectral_bin_size(self) -> int:
            """Get the spectral pixel bin size.

            Returns
            -------
            int
                Spectral pixel bin size.

            """
            return int(np.median(self.spectral_pixel_bin_width))

        @property
        def spectral_bin_offset(self) -> int:
            """Get the spectral pixel bin offset.

            Returns
            -------
            int
                Spectral pixel bin offset.

            """
            return self.spectral_pixel_low[0, 0]

        @property
        def bin_table_name(self) -> str:
            """Get the name of the bin table used in this file.

            Returns
            -------
            str
                The name of the bin table.

            """
            return self._binning['bintablename'][0]

    class SpacecraftGeometry:
        """A data structure representing the "spacecraftgeometry" bin table.

        Parameters
        ----------
        spacecraft_geometry
            The spacecraft geometry structure.

        """

        def __init__(self, spacecraft_geometry):
            self._spacecraft_geometry = spacecraft_geometry.data

        @property
        def sub_spacecraft_latitude(self) -> np.ndarray:
            """Get the sub-spacecraft latitude [degrees] of each integration.

            Returns
            -------
            np.ndarray
                Sub-spacecraft latitude of each integration.

            """
            return self._spacecraft_geometry['sub_spacecraft_lat']

        @property
        def sub_spacecraft_longitude(self) -> np.ndarray:
            """Get the sub-spacecraft longitude [degrees] of each integration.

            Returns
            -------
            np.ndarray
                Sub-spacecraft longitude of each integration.

            """
            return self._spacecraft_geometry['sub_spacecraft_lon']

        @property
        def sub_solar_latitude(self) -> np.ndarray:
            return self._spacecraft_geometry['sub_solar_lat']

        @property
        def sub_solar_longitude(self) -> np.ndarray:
            return self._spacecraft_geometry['sub_solar_lon']

        @property
        def sub_solar_altitude(self) -> np.ndarray:
            return self._spacecraft_geometry['sub_solar_alt']

        @property
        def spacecraft_position_vector(self) -> np.ndarray:
            return self._spacecraft_geometry['v_spacecraft']

        @property
        def spacecraft_velocity_vector(self) -> np.ndarray:
            return self._spacecraft_geometry['v_spacecraft_rate']

        @property
        def sun_position_vector(self) -> np.ndarray:
            """Get the position of the sun relative to Mars' center of mass
            [km].

            Returns
            -------
            np.ndarray
                Position of the sun.

            """
            return self._spacecraft_geometry['v_sun']

        @property
        def sun_velocity_vector(self) -> np.ndarray:
            """Get the velocity of the sun relative to Mars' center of mass
            [km/s].

            Returns
            -------
            np.ndarray
                Position of the sun.

            """
            return self._spacecraft_geometry['v_sun_rate']

        @property
        def spacecraft_x_unit_vector(self):
            return self._spacecraft_geometry['v_sun_rate']

        @property
        def inertial_frame_instrument_x_unit_vector(self) -> np.ndarray:
            """Get the unit vector of the "x" component of the instrument in the
            inertial frame of each integration.

            Returns
            -------
            np.ndarray
                "x" component of the instrument velocity in the inertial frame.

            """
            return self._spacecraft_geometry['vx_instrument_inertial']

        @property
        def inertial_frame_spacecraft_velocity_vector(self) -> np.ndarray:
            """Get the spacecraft velocity vector [km/s] in the inertial frame of
            each integration.

            Returns
            -------
            np.ndarray
                Spacecraft velocity vector in the inertial frame.

            """
            return self._spacecraft_geometry['v_spacecraft_rate_inertial']

    class PixelGeometry(_FitsRecord):
        """Get the arrays of the pixel geometry.

        Parameters
        ----------
        pixel_geometry
            The pixelgeometry structure.

        Notes
        -----
        The last dimension has 5 elements. These indices are described as
        follows:

        0. The bottom left corner
        1. The top left corner
        2. The bottom right corner
        3. The top right corner
        4. The pixel center

        """
        def __init__(self, pixel_geometry: fits.fitsrec.FITS_rec):
            super().__init__()
            self._pixel_geometry = pixel_geometry.data

        @property
        @app_flip
        def vector(self) -> np.ndarray:
            """Get the unit vector of each spatial pixel corner.

            Returns
            -------
            np.ndarray
                Unit vector of each spatial pixel corner.

            Notes
            -----
            For whatever reason, this has shape in the data of
            (number of integrations, 3, number of positions, 5). I rearranged
            the axes so that this has shape
            (number of integrations, number of positions, 5, 3) so it now
            matches the same shapes as all the other arrays.

            """
            pixel_vec = self._pixel_geometry['pixel_vec']
            reshaped_pixel_vec = np.moveaxis(pixel_vec, 1, -1)
            return reshaped_pixel_vec[None, :] if np.ndim(reshaped_pixel_vec) \
                == 3 else reshaped_pixel_vec


        @property
        @app_flip
        @add_integration_dimension
        def right_ascension(self) -> np.ndarray:
            """Get the right ascension [degrees] of each spatial pixel corner.

            Returns
            -------
            np.ndarray
                Right ascension of each spatial pixel corner.

            """
            return self._pixel_geometry['pixel_corner_ra']

        @property
        @app_flip
        @add_integration_dimension
        def declination(self) -> np.ndarray:
            """Get the declination [degrees] of each spatial pixel corner.

            Returns
            -------
            np.ndarray
                Declination of each spatial pixel corner.

            """
            return self._pixel_geometry['pixel_corner_dec']

        @property
        @app_flip
        @add_integration_dimension
        def latitude(self) -> np.ndarray:
            """Get the latitude [degrees] of each spatial pixel corner.

            Returns
            -------
            np.ndarray
                Latitude of each spatial pixel corner.

            """
            return self._pixel_geometry['pixel_corner_lat']

        @property
        @app_flip
        @add_integration_dimension
        def longitude(self) -> np.ndarray:
            """Get the longitude [degrees] of each spatial pixel corner.

            Returns
            -------
            np.ndarray
                Longitude of each spatial pixel corner.

            """
            return self._pixel_geometry['pixel_corner_lon']

        @property
        @app_flip
        @add_integration_dimension
        def tangent_altitude(self) -> np.ndarray:
            """Get the altitude [km] of each spatial pixel corner.

            Returns
            -------
            np.ndarray
                Altitude of each spatial pixel corner.

            """
            return self._pixel_geometry['pixel_corner_mrh_alt']

        @property
        @app_flip
        @add_integration_dimension
        def altitude_rate(self) -> np.ndarray:
            """Get the altitude rate [km/s] of each spatial pixel corner.

            Returns
            -------
            np.ndarray
                Altitude rate of each spatial pixel corner.

            """
            return self._pixel_geometry['pixel_corner_mrh_alt_rate']

        @property
        @app_flip
        @add_integration_dimension
        def line_of_sight(self) -> np.ndarray:
            """Get the line of sight [km] of each spatial pixel corner.

            Returns
            -------
            np.ndarray
                Line of sight of each spatial pixel corner.

            """
            return self._pixel_geometry['pixel_corner_los']

        @property
        @app_flip
        @add_integration_dimension
        def solar_zenith_angle(self) -> np.ndarray:
            """Get the solar zenith angle [degrees] of each spatial pixel.

            Returns
            -------
            np.ndarray
                Solar zenith angle of each spatial pixel.

            """
            return self._pixel_geometry['pixel_solar_zenith_angle']

        @property
        @app_flip
        @add_integration_dimension
        def emission_angle(self) -> np.ndarray:
            """Get the emission angle [degrees] of each spatial pixel.

            Returns
            -------
            np.ndarray
                Emission angle of each spatial pixel.

            """
            return self._pixel_geometry['pixel_emission_angle']

        @property
        @app_flip
        @add_integration_dimension
        def phase_angle(self) -> np.ndarray:
            """Get the phase angle [degrees] of each spatial pixel.

            Returns
            -------
            np.ndarray
                Phase angle of each spatial pixel.

            """
            return self._pixel_geometry['pixel_phase_angle']

        @property
        @app_flip
        @add_integration_dimension
        def zenith_angle(self) -> np.ndarray:
            """Get the zenith angle [degrees] of each spatial pixel.

            Returns
            -------
            np.ndarray
                Zenith angle of each spatial pixel.

            """
            return self._pixel_geometry['pixel_zenith_angle']

        @property
        @app_flip
        @add_integration_dimension
        def local_time(self) -> np.ndarray:
            """Get the local time [hours] of each spatial pixel.

            Returns
            -------
            np.ndarray
                Local time of each spatial pixel.

            """
            return self._pixel_geometry['pixel_local_time']

    class Observation:
        """A data structure representing the "observation" record arrays.

        Parameters
        ----------
        observation
            The observation structure.

        """
        def __init__(self, observation):
            self._observation = observation

        @property
        def integration_time(self) -> np.float32:
            """Get the integration time corresponding to this observation.

            Returns
            -------
            str
                The integration time.

            """
            return self._observation['int_time']

        @property
        def channel(self) -> str:
            """Get the channel corresponding to this observation.

            Returns
            -------
            str
                The channel name.

            """
            return self._observation['channel']

        @property
        def voltage(self) -> np.float32:
            """Get the MCP voltage [V] settings used to collect data in this
            file.

            Returns
            -------
            np.ndarray
                MCP voltage settings.

            """
            return self._observation['mcp_volt'][0]

        @property
        def voltage_gain(self) -> np.float32:
            """Get the MCP voltage gain settings used to collect data in this
            file.

            Returns
            -------
            np.ndarray
                MCP voltage gain settings.

            """
            return self._observation['mcp_gain'][0]

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
            return self._observation['wavelength'][0]

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
            return self._observation['wavelength_width'][0]

    @property
    def detector_image(self) -> DetectorImage:
        """Get the detector image substructure.

        Returns
        -------
        DetectorImage
            The detector image.

        """
        return self._detector_image

    @property
    def integration(self) -> Integration:
        """Get the integration substructure.

        Returns
        -------
        Integration
            The integration.

        """
        return self._integration

    @property
    def binning(self) -> Binning:
        """Get the binning substructure.

        Returns
        -------
        Binning
            The binning.

        """
        return self._binning

    @property
    def spacecraft_geometry(self) -> SpacecraftGeometry:
        """Get the spacecraft geometry structure.

        Returns
        -------
        SpacecraftGeometry
            The spacecraft geometry structure.

        """
        return self._spacecraft_geometry

    @property
    def pixel_geometry(self) -> PixelGeometry:
        """Get the pixel geometry substructure.

        Returns
        -------
        PixelGeometry
            The pixel geometry.

        """
        return self._pixel_geometry

    @property
    def observation(self) -> Observation:
        """Get the observation substructure.

        Returns
        -------
        Observation
            The observation information.

        """
        return self._observation

    @property
    def dark_integration(self) -> Integration:
        """Get the dark integration substructure.

        Returns
        -------
        Integration
            The dark integration.

        """
        return self._dark_integration

    @property
    def dark_observation(self) -> Observation:
        """Get the observation substructure.

        Returns
        -------
        Observation
            The observation information.

        """
        return self._dark_observation

    @property
    def flip(self):
        return self._flip

    def is_app_flipped(self) -> bool:
        """Determine if the APP was flipped.

        Returns
        -------
        bool
            True if the APP was flipped; False otherwise.

        """
        dot_product = np.dot(
            self.spacecraft_geometry.inertial_frame_instrument_x_unit_vector[
                -1],
            self.spacecraft_geometry.inertial_frame_spacecraft_velocity_vector[
                -1])
        return np.sign(dot_product) > 0

    def is_dayside_file(self) -> bool:
        """Determine if the input file is a file taken with dayside settings.

        Returns
        -------
        bool
            True if the file is a dayside file; False otherwise.

        """
        return self.observation.voltage < day_night_voltage_boundary

    def is_relay_file(self) -> bool:
        """Determine if the input file is a relay file.

        Returns
        -------
        bool
            True if the file is a relay file; False otherwise.

        """
        return np.amin(self.integration.mirror_angle_degree) == minimum_mirror_angle \
               and np.amax(
            self.integration.mirror_angle_degree) == maximum_mirror_angle


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
    from pyuvs.data_files0.path import find_latest_apoapse_muv_file_paths_from_block
    p = Path('/media/kyle/Samsung_T5/IUVS_Data')
    files = find_latest_apoapse_muv_file_paths_from_block(p, 5675)
    l = L1bFile(files[0])
    print(l.flip, l.is_relay_file())
