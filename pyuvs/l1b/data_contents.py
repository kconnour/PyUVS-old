"""The data_contents module contains classes to extract info from an L1b data
file.
"""
from astropy.io import fits
import numpy as np
from pyuvs.files import DataFilename


class _IUVSDataContents:
    """Hold the contents common to all IUVS data files.

    _IUVSDataContents holds the primary info and provides methods common to
    .fits files.

    """
    def __init__(self, hdulist: fits.hdu.hdulist.HDUList) -> None:
        """
        Parameters
        ----------
        hdulist
            The opened .fits file.

        Raises
        ------
        IndexError
            Raised if :code:`hdulist`'s primary structure does not have
            dimensions of 2 or 3.

        """
        self.hdulist = hdulist
        self.__primary_shape = self.__primary_shape()

    def __primary_shape(self) -> tuple[int, int, int]:
        ndims = np.ndim(self.primary)
        if ndims == 2:
            return self.primary[np.newaxis, :, :].shape
        elif ndims == 3:
            return self.primary.shape
        else:
            message = f'This file has {ndims} dimensions, not the standard 2 ' \
                      f'or 3. Unsure how to deal with this file...'
            raise IndexError(message)

    def info(self) -> None:
        """ Print info about the input file.

        """
        self.hdulist.info()

    @property
    def primary(self) -> np.ndarray:
        """ Get the "PRIMARY" data structure.

        """
        return self.hdulist['primary'].data

    @property
    def n_integrations(self) -> int:
        """ Get the number of integrations in this observation file.

        """
        return self.__primary_shape[0]

    @property
    def n_positions(self) -> int:
        """ Get the number of detector positions in this observation file.

        """
        return self.__primary_shape[1]

    @property
    def n_wavelengths(self) -> int:
        """ Get the number of wavelengths used in this observation file.

        """
        return self.__primary_shape[2]


# TODO: add columns
class _L1bIntegrationContents:
    """Hold the contents in the "Integration" structure.

    """
    def __init__(self, hdulist: fits.hdu.hdulist.HDUList) -> None:
        """
        Parameters
        ----------
        hdulist
            The opened .fits file.

        Notes
        -----
        The following columns are in "Integration"
        - Timestamp (missing)
        - ET (missing)
        - UTC (missing)
        - mirror_dn (missing)
        - mirror_deg
        - fov_deg (missing)
        - lya_centroid (missing)
        - det_temp_c (missing)
        - case_temp_c (missing)

        """
        self.__hdulist = hdulist

    def print_integration_columns(self) -> None:
        """ Print the columns in the "Integration" structure.

        """
        print(self.__get_integration().columns)

    def __get_integration(self) -> fits.fitsrec.FITS_rec:
        return self.__hdulist['integration'].data

    @property
    def mirror_angles(self) -> np.ndarray:
        """ Get the file's mirror angles [degrees].

        """
        return self.__get_integration()['mirror_deg']


# TODO: add columns
class _L1bObservationContents:
    """ Hold the contents in the "Observation" structure.

    """
    def __init__(self, hdulist: fits.hdu.hdulist.HDUList) -> None:
        """
        Parameters
        ----------
        hdulist
            The opened .fits file.

        Notes
        -----
        The following columns are in "Observation"
        - product_id (missing)
        - collection_id (missing)
        - bundle_id (missing)
        - code_svn_revision (missing)
        - anc_svn_revision (missing)
        - product_creation_date (missing)
        - observation_type (missing)
        - mission_phase (missing)
        - target_name (missing)
        - orbit_segment (missing)
        - orbit_number
        - solar_longitude
        - grating_select (missing)
        - keyhold_select (missing)
        - bin_pattern_index (missing)
        - cadence (missing)
        - int_time (missing)
        - duty_cycle (missing)
        - channel (missing)
        - wavelength
        - wavelength_width (missing)
        - kernels (missing)
        - mcp_volt
        - mcp_gain (missing)
        - dark_method (missing)
        - dark_files (missing)
        - calibration_version (missing)

        """
        self.__hdulist = hdulist

    def print_observation_columns(self) -> None:
        """ Print the columns in the "Observation" structure.

        """
        print(self.__get_observation().columns)

    def __get_observation(self) -> fits.fitsrec.FITS_rec:
        return self.__hdulist['observation'].data

    @property
    def orbit_number(self) -> int:
        """ Get the orbit number.

        """
        return self.__get_observation()['orbit_number'][0]

    @property
    def solar_longitude(self) -> float:
        """ Get the Ls used for each integration [degrees].

        """
        return self.__get_observation()['solar_longitude'][0]

    @property
    def wavelength(self) -> np.ndarray:
        """ Get the wavelengths used in this data file.

        Notes
        ----
        The wavelength will have shape (n_positions, n_wavelengths).

        """
        return self.__get_observation()['wavelength']

    @property
    def mcp_volt(self) -> float:
        """ Get the voltage gain used in the observation.

        """
        return self.__get_observation()['mcp_volt'][0]


class _L1bSpacecraftGeometry:
    def __init__(self, hdulist: fits.hdu.hdulist.HDUList) -> None:
        self.__hdulist = hdulist

    def print_spacecraftgeometry_columns(self) -> None:
        """ Print the columns in the "SpacecraftGeometry" structure.

        """
        print(self.__get_spacecraftgeometry().columns)

    def __get_spacecraftgeometry(self) -> fits.fitsrec.FITS_rec:
        return self.__hdulist['spacecraftgeometry'].data

    @property
    def vx_instrument_inertial(self) -> np.ndarray:
        return self.__get_spacecraftgeometry()['vx_instrument_inertial']

    @property
    def v_spacecraft_rate_inertial(self) -> np.ndarray:
        return self.__get_spacecraftgeometry()['v_spacecraft_rate_inertial']

    @property
    def sub_solar_lon(self) -> np.ndarray:
        return self.__get_spacecraftgeometry()['sub_solar_lon']


# TODO: add columns
class _L1bPixelgeometryContents:
    """ Hold the contents of the "Pixelgeometry" structure.

    """
    def __init__(self, hdulist: fits.hdu.hdulist.HDUList) -> None:
        """
        Parameters
        ----------
        hdulist
            The opened .fits file.

        Notes
        -----
        The following columns are in "Pixelgeometry"
        - pixel_vec (missing)
        - pixel_corner_ra (missing)
        - pixel_corner_dec (missing)
        - pixel_corner_lat
        - pixel_corner_lon
        - pixel_corner_mrh_alt
        - pixel_corner_mrh_alt_rate (missing)
        - pixel_corner_los (missing)
        - pixel_solar_zenith_angle
        - pixel_emission_angle
        - pixel_zenith_angle (missing)
        - pixel_phase_angle
        - pixel_local_time

        """
        self.__hdulist = hdulist

    def print_pixelgeometry_columns(self) -> None:
        """ Print the columns in the "Pixelgeometry" structure.

        """
        print(self.__get_pixelgeometry().columns)

    def __get_pixelgeometry(self) -> fits.fitsrec.FITS_rec:
        return self.__hdulist['pixelgeometry'].data

    @property
    def latitude(self) -> np.ndarray:
        """ Get the latitude of each pixel in the observation.

        """
        return self.__get_pixelgeometry()['pixel_corner_lat']

    @property
    def longitude(self) -> np.ndarray:
        """ Get the longitude of each pixel in the observation.

        """
        return self.__get_pixelgeometry()['pixel_corner_lon']

    @property
    def altitude(self) -> np.ndarray:
        """ Get the tangent altitude of each pixel in the observation.

        """
        return self.__get_pixelgeometry()['pixel_corner_mrh_alt']

    @property
    def solar_zenith_angle(self) -> np.ndarray:
        """ Get the solar zenith angles of each pixel in the observation.

        """
        return self.__get_pixelgeometry()['pixel_solar_zenith_angle']

    @property
    def emission_angle(self) -> np.ndarray:
        """ Get the emission angle of each pixel in the observation.

        """
        return self.__get_pixelgeometry()['pixel_emission_angle']

    @property
    def phase_angle(self) -> np.ndarray:
        """ Get the phase angle of each pixel in the observation.

        """
        return self.__get_pixelgeometry()['pixel_phase_angle']

    @property
    def local_time(self) -> np.ndarray:
        """ Get the local time of each pixel in the observation.

        """
        return self.__get_pixelgeometry()['pixel_local_time']


'''class L1bDataContents(_IUVSDataContents,
                      _L1bIntegrationContents,
                      _L1bSpacecraftGeometry,
                      _L1bPixelgeometryContents,
                      _L1bObservationContents):
    """ An L1bDataContents object can retrieve info from the contents of an
    IUVS l1b data file. The following are the parts of an L1b file:

    0. PRIMARY
    1. Random_dn_unc
    2. Random_phy_unc
    3. Systematic_phy_unc
    4. detector_raw
    5. detector_dark_subtracted
    6. quality_flag
    7. background_dark
    8. Dark_Integration
    9. Dark_Engineering
    10. Dark_Observation
    11. dectector_dark
    12. Integration
    13. Engineering
    14. Binning
    15. SpacecraftGeometry
    16. PixelGeometry
    17. Observation

    Not all of these are included in this class. Some are missing properties.
    Some properties are renamed because I believe the names in the data products
    themselves are sometimes poorly named.

    Nevertheless, this is a convenience data structure so you don't have to work
    with a .fits file directly.

    """
    def __init__(self, filename: DataFilename) -> None:
        """
        Parameters
        ----------
        filename
            A single IUVS data filename.

        """
        hdulist = fits.open(filename.path)
        _IUVSDataContents.__init__(self, hdulist)
        _L1bIntegrationContents.__init__(self, hdulist)
        _L1bSpacecraftGeometry.__init__(self, hdulist)
        _L1bPixelgeometryContents.__init__(self, hdulist)
        _L1bObservationContents.__init__(self, hdulist)'''


class L1bDataContents:
    def __init__(self, filename: DataFilename) -> None:
        """

        Parameters
        ----------
        filename
        """
        self.__hdulist = fits.open(filename.path)
        self.__primary_shape = self.__primary_shape()

    def __primary_shape(self) -> tuple[int, int, int]:
        primary = self.__hdulist['primary'].data
        ndims = np.ndim(primary)
        if ndims == 2:
            return primary[np.newaxis, :, :].shape
        elif ndims == 3:
            return primary.shape
        else:
            message = f'This file has {ndims} dimensions, not the standard 2 ' \
                      f'or 3. Unsure how to deal with this file...'
            raise IndexError(message)

    def __getattr__(self, method):
        return getattr(self.val, method)

    def __getitem__(self, x):
        return self.__hdulist[x]

    def info(self) -> None:
        """ Print info about the input file.

        """
        self.__hdulist.info()

    @property
    def n_integrations(self) -> int:
        """ Get the number of integrations in this observation file.

        """
        return self.__primary_shape[0]

    @property
    def n_positions(self) -> int:
        """ Get the number of detector positions in this observation file.

        """
        return self.__primary_shape[1]

    @property
    def n_wavelengths(self) -> int:
        """ Get the number of wavelengths used in this observation file.

        """
        return self.__primary_shape[2]

    @property
    def hdulist(self) -> fits.hdu.hdulist.HDUList:
        return self.__hdulist
