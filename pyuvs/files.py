import glob
from astropy.io import fits
import numpy as np


def get_filenames(path: str, segment: str, orbit: int, channel: str) -> list[str]:
    return sorted(glob.glob(f'{path}/*{segment}*{orbit}*{channel}*.fits.gz'))


def get_apoapse_muv_filenames(path: str, orbit: int) -> list[str]:
    return get_filenames(path, 'apoapse', orbit, 'muv')


class L1bFile:
    def __init__(self, filepath: str):
        hdul = fits.open(filepath)
        self.primary = self._get_primary(hdul)
        self.pixelgeometry = _Pixelgeometry(self._get_pixelgeometry(hdul))

        del hdul

    @staticmethod
    def _get_primary(hdul):
        return hdul['primary'].data

    @staticmethod
    def _get_pixelgeometry(hdul):
        return hdul['pixelgeometry'].data


class _Pixelgeometry:
    def __init__(self, structure: fits.fitsrec.FITS_rec):
        self.structure = structure

        self.latitude = self._get_latitude()
        self.longitude = self._get_longitude()
        self.altitude = self._get_altitude()
        self.solar_zenith_angle = self._get_solar_zenith_angle()
        self.emission_angle = self._get_emission_angle()
        self.phase_angle = self._get_phase_angle()
        self.zenith_angle = self._get_zenith_angle()
        self.local_time = self._get_local_time()
        self.right_ascension = self._get_right_ascension()
        self.declination = self._get_declination()
        self.altitude_rate = self._get_altitude_rate()
        self.line_of_sight = self._get_line_of_sight()
        self.vector = self._get_vector()

        del self.structure

    def _get_latitude(self) -> np.ndarray:
        return self._get_substructure('pixel_corner_lat')

    def _get_longitude(self) -> np.ndarray:
        return self._get_substructure('pixel_corner_lon')

    def _get_altitude(self) -> np.ndarray:
        return self._get_substructure('pixel_corner_mrh_alt')

    def _get_solar_zenith_angle(self) -> np.ndarray:
        return self._get_substructure('pixel_solar_zenith_angle')

    def _get_emission_angle(self) -> np.ndarray:
        return self._get_substructure('pixel_emission_angle')

    def _get_phase_angle(self) -> np.ndarray:
        return self._get_substructure('pixel_phase_angle')

    def _get_local_time(self) -> np.ndarray:
        return self._get_substructure('pixel_local_time')

    def _get_zenith_angle(self) -> np.ndarray:
        return self._get_substructure('pixel_zenith_angle')

    def _get_right_ascension(self) -> np.ndarray:
        return self._get_substructure('pixel_corner_ra')

    def _get_declination(self) -> np.ndarray:
        return self._get_substructure('pixel_corner_dec')

    def _get_altitude_rate(self) -> np.ndarray:
        return self._get_substructure('pixel_corner_mrh_alt_rate')

    def _get_line_of_sight(self) -> np.ndarray:
        return self._get_substructure('pixel_corner_los')

    def _get_vector(self) -> np.ndarray:
        return self._get_substructure('pixel_vec')

    def _get_substructure(self, name: str) -> np.ndarray:
        return self.structure[name]
