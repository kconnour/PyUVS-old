# 3rd-party imports
from astropy.io import fits
import numpy as np

# Local imports
from pyuvs.files import DataFilename


class IUVSDataContents:
    """ An IUVS DataContents object will open a IUVS .fits file and provide
    methods to get some of its content. """
    def __init__(self, filename: str) -> None:
        self.hdulist = fits.open(filename)
        self.__primary_shape = self.__primary_shape()

    def __primary_shape(self):
        if np.ndim(self.primary) == 2:
            return self.primary[np.newaxis, :, :].shape
        elif np.ndim(self.primary) == 3:
            return self.primary.shape
        else:
            raise IndexError(
                f'This file has {np.ndim(self.primary)} dimensions, not the '
                f'standard 2 or 3. Unsure how to deal with this file...')

    def info(self):
        """ Print info about the input file.

        Returns
        -------
        None
        """
        self.hdulist.info()

    @property
    def primary(self):
        """ Get the primary data structure.

        Returns
        -------
        primary: np.ndarray
            The primary structure.

        """
        return self.hdulist['primary'].data

    @property
    def n_integrations(self):
        """ Get the number of integrations of this observation file.

        Returns
        -------
        n_integrations: int
            The number of integrations.

        """
        return self.__primary_shape[0]

    @property
    def n_positions(self):
        """ Get the number of detector positions of this observation file.

        Returns
        -------
        n_positions: int
            The number of positions.

        """
        return self.__primary_shape[1]

    @property
    def n_wavelengths(self):
        """ Get the number of wavelengths of this observation file.

        Returns
        -------
        n_wavelengths: int
            The number of wavelengths

        """
        return self.__primary_shape[2]

    @staticmethod
    def _print_column(column):
        print(column.columns)


class L1bIntegrationContents(IUVSDataContents):
    """ An L1bIntegrationContents object can get info from the "integration"
    structure within IUVS l1b files. It is not meant to be used by itself. """
    def __init__(self, filename):
        super().__init__(filename)
        # Note: this class is only meant to be used in L1bDataContents, so it
        # does not check that data are l1b data.
        # Note: setting self.__integration = self.__get_integration() causes
        # a significant slowdown, so I chose not to implement that.

    def print_integration_columns(self):
        """ Print the columns in the "integration" structure.
        Returns
        -------
        None
        """
        self._print_column(self.__get_integration())

    @property
    def mirror_angles(self):
        """ Get the file's mirror angles
        Returns
        -------
        mirror_angles: np.ndarray
            The file's mirror angles.
        """
        return self.__get_integration()['mirror_deg']

    def __get_integration(self):
        return self.hdulist['integration'].data


class L1bObservationContents(IUVSDataContents):
    """ An L1bObservationContents object can get info from the "observation"
    structure within IUVS l1b files. It is not meant to be used by itself. """
    def __init__(self, filename: str) -> None:
        super().__init__(filename)
        # Note: this class is only meant to be used in L1bDataContents, so it
        # does not check that data are l1b data.
        # Note: setting self.__observation = self.__get_observation() causes
        # a significant slowdown, so I chose not to implement that.

    def print_observation_columns(self):
        """ Print the columns in the "observation" structure.
        Returns
        -------
        None
        """
        self._print_column(self.__get_observation())

    @property
    def voltage(self):
        """ Get the voltage gain used in the observation.
        Returns
        -------
        voltage: float
            The voltage gain.
        """
        return self.__get_observation()['mcp_volt'][0]

    @property
    def wavelengths(self):
        """ Get the wavelengths used for each integration.
        Returns
        -------
        wavelengths: np.ndarray
            The wavelengths.
        """
        return self.__get_observation()['wavelength']

    @property
    def solar_longitude(self):
        """ Get the Ls used for each integration.
        Returns
        -------
        wavelengths: np.ndarray
            The wavelengths.
        """
        return self.__get_observation()['solar_longitude']

    def __get_observation(self):
        return self.hdulist['observation'].data


class L1bPixelgeometryContents(IUVSDataContents):
    """ An L1bPixeleometryContents object can get info from the "pixelgeometry"
    structure within IUVS l1b files. It is not meant to be used by itself. """
    def __init__(self, filename):
        super().__init__(filename)
        # Note: this class is only meant to be used in L1bDataContents, so it
        # does not check that data are l1b data.
        # Note: setting self.__pixelgeometry = self.__get_pixelgeometry()
        # causes a significant slowdown, so I chose not to implement that.

    def print_pixelgeometry_columns(self):
        """ Print the columns in the "pixelgeometry" structure.
        Returns
        -------
        None
        """
        self._print_column(self.__get_pixelgeometry())

    @property
    def altitude(self):
        """ Get the tangent altitude of each pixel in the observation.
        Returns
        -------
        altitude: np.ndarray
            The pixel tangent altitudes.
        """
        return self.__get_pixelgeometry()['pixel_corner_mrh_alt']

    @property
    def latitude(self):
        """ Get the latitude of each pixel in the observation.
        Returns
        -------
        latitude: np.ndarray
            The pixel latitudes.
        """
        return self.__get_pixelgeometry()['pixel_corner_lat']

    @property
    def longitude(self):
        """ Get the longitude of each pixel in the observation.
        Returns
        -------
        longitude: np.ndarray
            The pixel longitudes.
        """
        return self.__get_pixelgeometry()['pixel_corner_lon']

    @property
    def local_time(self):
        """ Get the local time of each pixel in the observation.
        Returns
        -------
        local_time: np.ndarray
            The pixel local times.
        """
        return self.__get_pixelgeometry()['pixel_local_time']

    @property
    def emission_angle(self):
        """ Get the emission angle of each pixel in the observation.
        Returns
        -------
        emission_angle: np.ndarray
            The pixel emission angles.
        """
        return self.__get_pixelgeometry()['pixel_emission_angle']

    @property
    def phase_angle(self):
        """ Get the phase angle of each pixel in the observation.
        Returns
        -------
        phase_angle: np.ndarray
            The pixel phase angles.
        """
        return self.__get_pixelgeometry()['pixel_phase_angle']

    @property
    def solar_zenith_angle(self):
        """ Get the solar zenith angles of each pixel in the observation.
        Returns
        -------
        solar_zenith_angle: np.ndarray
            The pixel solar zenith angles.
        """
        return self.__get_pixelgeometry()['pixel_solar_zenith_angle']

    def __get_pixelgeometry(self):
        return self.hdulist['pixelgeometry'].data


class L1bDataContents(L1bIntegrationContents, L1bObservationContents,
                      L1bPixelgeometryContents):
    """ An L1bDataContents object can retrieve info from the contents of an
    IUVS l1b data file. """
    def __init__(self, filename):
        """
        Parameters
        ----------
        filename:
        """
        super().__init__(filename)
