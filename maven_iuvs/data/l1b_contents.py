# Local imports
from maven_iuvs.data.contents import DataContents


class L1bObservationContents(DataContents):
    def __init__(self, filename):
        super().__init__(filename)
        self.__observation = self.__get_observation()

    def __get_observation(self):
        return self.hdulist['observation'].data

    def print_observation_columns(self):
        self._print_column(self.__observation)

    @property
    def voltage(self):
        return self.__observation['mcp_volt'][0]

    @property
    def wavelengths(self):
        return self.__observation['wavelength']


class L1bPixelgeometryContents(DataContents):
    def __init__(self, filename):
        super().__init__(filename)
        self.__pixelgeometry = self.__get_pixelgeometry()

    def __get_pixelgeometry(self):
        return self.hdulist['pixelgeometry'].data

    def print_pixelgeometry_columns(self):
        self._print_column(self.__pixelgeometry)

    @property
    def altitude(self):
        return self.__pixelgeometry['pixel_corner_mrh_alt']

    @property
    def latitude(self):
        return self.__pixelgeometry['pixel_corner_lat']

    @property
    def longitude(self):
        return self.__pixelgeometry['pixel_corner_lon']

    @property
    def local_time(self):
        return self.__pixelgeometry['pixel_local_time']

    @property
    def emission_angle(self):
        return self.__pixelgeometry['pixel_emission_angle']

    @property
    def phase_angle(self):
        return self.__pixelgeometry['pixel_phase_angle']

    @property
    def solar_zenith_angle(self):
        return self.__pixelgeometry['pixel_solar_zenith_angle']


class L1bDataContents(L1bObservationContents, L1bPixelgeometryContents):
    def __init__(self, filename):
        super().__init__(filename)
