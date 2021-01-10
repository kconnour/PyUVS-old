# Built-in imports
import os

# 3rd-party imports
import numpy as np

# Local imports
from maven_iuvs.files.orbit_block import OrbitBlock


class DataPath(OrbitBlock):
    """ A DataPath object creates absolute paths to where data reside, given a
     set of assumptions. """
    def block_path(self, path, orbit):
        """ Make the path to an orbit, assuming orbits are organized in blocks
        of 100 orbits.

        Parameters
        ----------
        path: str
            The stem of the path where data are organized into blocks.
        orbit: int
            The orbit number.

        Returns
        -------
        path: str
            The path with orbit block corresponding to the input orbit.
        """
        return os.path.join(path, self.__make_orbit_block_folder_name(orbit))

    def orbit_block_paths(self, path, orbits):
        """ Make paths to orbits, assuming orbits are organized in blocks of
        100 orbits.

        Parameters
        ----------
        path: str
            The stem of the path where data are organized into blocks.
        orbits: list
            List of ints of orbits.

        Returns
        -------
        paths: list
            The path with orbit block corresponding to the input orbits.
        """
        return [self.block_path(path, f) for f in orbits]

    def __make_orbit_block_folder_name(self, orbit):
        rounded_orbit = self.__round_to_nearest_hundred(orbit)
        return f'orbit{self._orbit_to_string(rounded_orbit)}'

    @staticmethod
    def __round_to_nearest_hundred(orbit):
        return int(np.floor(orbit / 100) * 100)
