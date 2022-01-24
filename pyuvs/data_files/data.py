from pathlib import Path
from astropy.io import fits
import numpy as np


# TODO: methods should mimic hdul naming, @property should be good naming
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

        self.primary = \
            self._get_structures('primary')
        # TODO: random_dn_unc
        # TODO: random_phy_unc
        # TODO: systematic_phy_unc
        # TODO: detector_raw
        # TODO: detector_dark_subtracted
        # TODO: quality_flag
        # TODO: background_dark
        # TODO: dark_integration
        # TODO: dark_engineering
        # TODO: dark_observation
        # TODO: detector_dark
        self.integration = \
            Integration(self._get_structures('integration'))
        # TODO: engineering
        # TODO: binning
        self.spacecraft_geometry = \
            SpacecraftGeometry(self._get_structures('spacecraftgeometry'))
        self.pixel_geometry = \
            PixelGeometry(self._get_structures('pixelgeometry'))
        self.observation = \
            Observation(self._get_structures('observation'))

        del self.hdul

        self._minimum_mirror_angle = 30.2508544921875
        self._maximum_mirror_angle = 59.6502685546875

    def _get_structures(self, name: str) -> fits.fitsrec.FITS_rec:
        # or it returns np.ndarray
        return self.hdul[name].data

    @property
    def minimum_mirror_angle(self) -> float:
        return self._minimum_mirror_angle

    @property
    def maximum_mirror_angle(self) -> float:
        return self._maximum_mirror_angle

    def relay_file(self) -> bool:
        """Determine if the input file is a relay file.

        Returns
        -------
        bool
            True if the file is a relay file; False otherwise.

        """
        return np.amin(self.integration.mirror_angle) == \
            self.minimum_mirror_angle and \
            np.amax(self.integration.mirror_angle) == \
            self.maximum_mirror_angle

    def dayside_file(self) -> bool:
        """Determine if the input file is a file taken with dayside settings.

        Returns
        -------
        bool
            True if the file is a dayside file; False otherwise.

        """
        return self.observation.mcp_voltage < 790


class _FitsRecord:
    def __init__(self, structure: fits.fitsrec.FITS_rec):
        self.structure = structure

    def get_substructure(self, name: str):
        return self.structure[name]

    def delete_structure(self):
        del self.structure


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
    def vector(self) -> np.ndarray:
        """Get the unit vector of each spatial pixel corner.

        Returns
        -------
        np.ndarray
            Unit vector of each spatial pixel corner.

        """
        return self._pixel_vec

    @property
    def right_ascension(self) -> np.ndarray:
        """Get the right ascension [degrees] of each spatial pixel corner.

        Returns
        -------
        np.ndarray
            Right ascension of each spatial pixel corner.

        """
        return self._pixel_corner_ra

    @property
    def declination(self) -> np.ndarray:
        """Get the declination [degrees] of each spatial pixel corner.

        Returns
        -------
        np.ndarray
            Declination of each spatial pixel corner.

        """
        return self._pixel_corner_dec

    @property
    def latitude(self) -> np.ndarray:
        """Get the corner latitude [degrees] of each spatial pixel corner.

        Returns
        -------
        np.ndarray
            Latitude of each spatial pixel corner.

        """
        return self._pixel_corner_lat

    @property
    def longitude(self) -> np.ndarray:
        """Get the corner longitude [degrees] of each spatial pixel corner.

        Returns
        -------
        np.ndarray
            Longitude of each spatial pixel corner.

        """
        return self._pixel_corner_lon

    @property
    def tangent_altitude(self) -> np.ndarray:
        """Get the altitude [km] of each spatial pixel corner.

        Returns
        -------
        np.ndarray
            Altitude of each spatial pixel corner.

        """
        return self._pixel_corner_mrh_alt

    @property
    def altitude_rate(self) -> np.ndarray:
        """Get the altitude rate [km/s] of each spatial pixel corner.

        Returns
        -------
        np.ndarray
            Altitude rate of each spatial pixel corner.

        """
        return self._pixel_corner_mrh_alt_rate

    @property
    def line_of_sight(self) -> np.ndarray:
        """Get the line of sight [km] of each spatial pixel corner.

        Returns
        -------
        np.ndarray
            Line of sight of each spatial pixel corner.

        """
        return self._pixel_corner_los

    @property
    def get_solar_zenith_angle(self) -> np.ndarray:
        """Get the solar zenith angle [degrees] of each spatial pixel.

        Returns
        -------
        np.ndarray
            Solar zenith angle of each spatial pixel.

        """
        return self._pixel_solar_zenith_angle

    @property
    def emission_angle(self) -> np.ndarray:
        """Get the emission angle [degrees] of each spatial pixel.

        Returns
        -------
        np.ndarray
            Emission angle of each spatial pixel.

        """
        return self._pixel_emission_angle

    @property
    def zenith_angle(self) -> np.ndarray:
        """Get the zenith angle [degrees] of each spatial pixel.

        Returns
        -------
        np.ndarray
            Zenith angle of each spatial pixel.

        """
        return self._pixel_zenith_angle

    @property
    def phase_angle(self) -> np.ndarray:
        """Get the phase angle [degrees] of each spatial pixel.

        Returns
        -------
        np.ndarray
            Phase angle of each spatial pixel.

        """
        return self._pixel_phase_angle

    @property
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

        self._mcp_volt = \
            self.get_substructure('mcp_volt')[0]

        self.delete_structure()

    @property
    def mcp_voltage(self) -> np.float32:
        """Get the MCP voltage [V] settings used to collect data in this file.

        Returns
        -------
        np.ndarray
            MCP voltage settings.

        """
        return self._mcp_volt


if __name__ == '__main__':
    from pathlib import Path
    from pyuvs.data_files import find_latest_apoapse_muv_file_paths_from_block
    import time
    p = Path('/media/kyle/Samsung_T5/IUVS_data')
    files = find_latest_apoapse_muv_file_paths_from_block(p, 3453)
    t0 = time.time()
    hdul = fits.open(files[0])
    t1 = time.time()
    print(hdul['spacecraftgeometry'].data.columns)
    l1b = L1bFile(files[0])
    #t2 = time.time()
    #print(t2-t1, t1-t0)
    #print(l1b.spacecraft_geometry.inertial_frame_spacecraft_velocity[0, :])
