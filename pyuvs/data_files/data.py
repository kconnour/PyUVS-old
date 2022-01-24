from astropy.io import fits
import numpy as np

# beta flip
# relay swath
# dayside
# swath number

# TODO: Add docstrings with units!
class L1bFile:
    def __init__(self, filepath: str):
        self.hdul = fits.open(filepath)

        self.primary = self._get_primary()
        self.integration = _Integration(self._get_integration())
        self.pixelgeometry = _Pixelgeometry(self._get_pixelgeometry())

        del self.hdul

    def _get_primary(self) -> np.ndarray:
        return self._get_structures('primary')

    def _get_integration(self) -> fits.fitsrec.FITS_rec:
        return self._get_structures('integration')

    def _get_pixelgeometry(self) -> fits.fitsrec.FITS_rec:
        return self._get_structures('pixelgeometry')

    def _get_structures(self, name: str):
        return self.hdul[name].data


class _FitsRecord:
    def __init__(self, structure: fits.fitsrec.FITS_rec):
        self.structure = structure

    def get_substructure(self, name: str):
        return self.structure[name]

    def delete_structure(self):
        del self.structure


class _Integration(_FitsRecord):
    def __init__(self, structure: fits.fitsrec.FITS_rec):
        super().__init__(structure)

        self.timestamp = self.get_timestamp()
        self.ephemeris_time = self.get_ephemeris_time()
        self.utc = self.get_utc()
        self.mirror_data_number = self.get_mirror_data_number()
        self.mirror_angle = self.get_mirror_angle()
        self.field_of_view = self.get_field_of_view()
        self.lyman_alpha_centroid = self.get_lyman_alpha_centroid()
        self.detector_temperature = self.get_detector_temperature()
        self.case_temperature = self.get_case_temperature()

        self.delete_structure()

    def get_timestamp(self) -> np.ndarray:
        # sclk seconds
        return self.get_substructure('timestamp')

    def get_ephemeris_time(self) -> np.ndarray:
        # ET s  (ephemeris time seconds?)
        return self.get_substructure('et')

    def get_utc(self) -> np.ndarray:
        # UTC date string
        return self.get_substructure('utc')

    def get_mirror_data_number(self) -> np.ndarray:
        # unit is DN; bscale = 1; bzero = 32768
        return self.get_substructure('mirror_dn')

    def get_mirror_angle(self) -> np.ndarray:
        # degrees
        return self.get_substructure('mirror_deg')

    def get_field_of_view(self) -> np.ndarray:
        # degrees
        return self.get_substructure('fov_deg')

    def get_lyman_alpha_centroid(self) -> np.ndarray:
        # pixel
        return self.get_substructure('lya_centroid')

    def get_detector_temperature(self) -> np.ndarray:
        # degrees celsius
        return self.get_substructure('det_temp_c')

    def get_case_temperature(self) -> np.ndarray:
        # degrees celsius
        return self.get_substructure('case_temp_c')


class _Pixelgeometry(_FitsRecord):
    def __init__(self, structure: fits.fitsrec.FITS_rec):
        super().__init__(structure)

        self.latitude = self.get_latitude()
        self.longitude = self.get_longitude()
        self.altitude = self.get_altitude()
        self.solar_zenith_angle = self.get_solar_zenith_angle()
        self.emission_angle = self.get_emission_angle()
        self.phase_angle = self.get_phase_angle()
        self.zenith_angle = self.get_zenith_angle()
        self.local_time = self.get_local_time()
        self.right_ascension = self.get_right_ascension()
        self.declination = self.get_declination()
        self.altitude_rate = self.get_altitude_rate()
        self.line_of_sight = self.get_line_of_sight()
        self.vector = self.get_vector()

        self.delete_structure()

    def get_latitude(self) -> np.ndarray:
        return self.get_substructure('pixel_corner_lat')

    def get_longitude(self) -> np.ndarray:
        return self.get_substructure('pixel_corner_lon')

    def get_altitude(self) -> np.ndarray:
        return self.get_substructure('pixel_corner_mrh_alt')

    def get_solar_zenith_angle(self) -> np.ndarray:
        return self.get_substructure('pixel_solar_zenith_angle')

    def get_emission_angle(self) -> np.ndarray:
        return self.get_substructure('pixel_emission_angle')

    def get_phase_angle(self) -> np.ndarray:
        return self.get_substructure('pixel_phase_angle')

    def get_local_time(self) -> np.ndarray:
        return self.get_substructure('pixel_local_time')

    def get_zenith_angle(self) -> np.ndarray:
        return self.get_substructure('pixel_zenith_angle')

    def get_right_ascension(self) -> np.ndarray:
        return self.get_substructure('pixel_corner_ra')

    def get_declination(self) -> np.ndarray:
        return self.get_substructure('pixel_corner_dec')

    def get_altitude_rate(self) -> np.ndarray:
        return self.get_substructure('pixel_corner_mrh_alt_rate')

    def get_line_of_sight(self) -> np.ndarray:
        return self.get_substructure('pixel_corner_los')

    def get_vector(self) -> np.ndarray:
        return self.get_substructure('pixel_vec')


if __name__ == '__main__':
    from pathlib import Path
    from pyuvs.data_files import find_latest_apoapse_muv_file_paths_from_block
    import time
    p = Path('/Volumes/Samsung_T5/IUVS_data')
    files = find_latest_apoapse_muv_file_paths_from_block(p, 3453)
    t0 = time.time()
    hdul = fits.open(files[0])
    t1 = time.time()
    #print(hdul['integration'].data.columns)
    #i = hdul['integration'].data
    l1b = L1bFile(files[0])
    t2 = time.time()
    print(t2-t1, t1-t0)
    #print(l1b.integration.timestamp.shape)
