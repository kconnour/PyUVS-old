"""The geography module contains classes to compute geographic information.
"""
import numpy as np


class Geography:
    """Get info to work with Martian geography.

    Geography contains several defined locations and can get distances on Mars.

    """
    def __init__(self):
        """

        """
        self.__locations = self.__make_locations()

    @staticmethod
    def __make_locations() -> dict[str, tuple[float, float]]:
        locations = {'arsia_mons': (-8.35, 239.91),
                     'ascraeus_mons': (11.92, 255.92),
                     'gale_crater': (-5.24, 127.48),
                     'olympus_mons': (18.39, 226.12),
                     'pavonis_mons': (1.48, 247.04)}
        return locations


    @property
    def locations(self) -> dict[str, tuple[float, float]]:
        """Get the known named locations. Each location is
        [degrees north, degrees east].

        """
        return self.__locations

    @staticmethod
    def __haversine(latitudes: np.ndarray, longitudes: np.ndarray,
                    target_lat: float, target_lon: float) -> np.ndarray:
        d_lat = np.radians(latitudes - target_lat)
        d_lon = np.radians(longitudes - target_lon)
        return np.sin(d_lat / 2) ** 2 + np.cos(np.radians(target_lat)) * np.cos(
            np.radians(latitudes)) * np.sin(d_lon / 2) ** 2

    def spatial_distance(self, latitudes: np.ndarray, longitudes: np.ndarray,
                         target_lat: float, target_lon: float) -> np.ndarray:
        """Compute the distance [km] between an array of latitudes and
        longitudes and a target point.

        Parameters
        ----------
        latitudes
            The latitudes.
        longitudes
            The longitudes.
        target_lat
            The target latitude.
        target_lon
            The target longitude.

        """
        return self.__r_mars * self.angular_distance(latitudes, longitudes,
                                                     target_lat, target_lon)

    def angular_distance(self, latitudes: np.ndarray, longitudes: np.ndarray,
                         target_lat: float, target_lon: float) -> np.ndarray:
        """Compute the distance [radians] between an array of latitudes and
        longitudes and a target point.

        Parameters
        ----------
        latitudes
            The latitudes.
        longitudes
            The longitudes.
        target_lat
            The target latitude.
        target_lon
            The target longitude.

        """
        arg = self.__haversine(latitudes, longitudes, target_lat, target_lon)
        return 2 * np.arcsin(np.sqrt(arg))

    def get_location_indices(self, latitudes: np.ndarray,
                             longitudes: np.ndarray,
                             target_lat: float, target_lon: float,
                             threshold: float) -> np.ndarray:
        """Get the indices of the latitudes and longitudes that are within a
        threshold distance [km] of a target point.

        Parameters
        ----------
        latitudes
            The latitudes.
        longitudes
            The longitudes.
        target_lat
            The target latitude.
        target_lon
            The target longitude.
        threshold
            The threshold distance.

        """
        dist = self.spatial_distance(latitudes, longitudes, target_lat,
                                     target_lon)
        return np.argwhere(dist <= threshold)

    def location_in_arrays(self, latitudes: np.ndarray, longitudes: np.ndarray,
                           target_lat: float, target_lon: float,
                           threshold: float) -> bool:
        """Determine whether there are any points in the latitudes and
        longitudes that are within a threshold distance from a target point.

        Parameters
        ----------
        latitudes
            The latitudes.
        longitudes
            The longitudes.
        target_lat
            The target latitude.
        target_lon
            The target longitude.
        threshold
            The threshold distance.

        """
        inds = self.get_location_indices(latitudes, longitudes, target_lat,
                                         target_lon, threshold)
        return inds.size > 0
