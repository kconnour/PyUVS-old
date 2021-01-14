# Built-in imports
import os
from pathlib import Path

# 3rd-party imports
import numpy as np


class OrbitBlock:
    @staticmethod
    def _orbit_to_string(orbit):
        return str(orbit).zfill(5)


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


class PatternGlob(OrbitBlock):
    """ A PatternGlob object creates glob search patterns tailored to IUVS
    data. """
    def pattern(self, orbit, segment, channel, extension='fits'):
        """ Make a glob pattern for an orbit, segment, and channel.

        Parameters
        ----------
        orbit: str or int
            The orbit to get data from. Can be '*' to get all orbits.
        segment: str or int
            The segment to get data from. Can be '*' to get all segments.
        channel: str or int
            The channel to get data from. Can be '*' to get all channels.
        extension: str
            The file extension to use. Default is 'fits'

        Returns
        -------
        pattern: str
            The glob pattern that matches the input parameters.
        """
        if orbit == '*':
            pattern = f'*{segment}-*-{channel}*.{extension}*'
        else:
            pattern = f'*{segment}-*{self._orbit_to_string(orbit)}-' \
                      f'{channel}*.{extension}*'
        return self.__remove_recursive_glob_pattern(pattern)

    def recursive_pattern(self, orbit, segment, channel):
        """ Make a recursive glob pattern for an orbit, segment, and channel.

        Parameters
        ----------
        orbit: str or int
            The orbit to get data from. Can be '*' to get all orbits.
        segment: str or int
            The segment to get data from. Can be '*' to get all segments.
        channel: str or int
            The channel to get data from. Can be '*' to get all channels.

        Returns
        -------
        pattern: str
            The recursive glob pattern that matches the input parameters.
        """
        pattern = self.pattern(orbit, segment, channel)
        return self.__prepend_recursive_glob_pattern(pattern)

    def orbit_patterns(self, orbits, segment, channel):
        """ Make glob patterns for each orbit in a list of orbits.

        Parameters
        ----------
        orbits: list
            List of ints or strings of orbits to make patterns for.
        segment: str or int
            The segment to get data from. Can be '*' to get all segments.
        channel: str or int
            The channel to get data from. Can be '*' to get all channels.

        Returns
        -------
        patterns: list
            List of patterns of len(orbits) that match the inputs.
        """
        orbs = [self._orbit_to_string(orbit) for orbit in orbits]
        return [self.pattern(orbit, segment, channel) for orbit in orbs]

    def recursive_orbit_patterns(self, orbits, segment, channel):
        """ Make recursive glob patterns for each orbit in a list of orbits.

        Parameters
        ----------
        orbits: list
            List of ints or strings of orbits to make patterns for.
        segment: str or int
            The segment to get data from. Can be '*' to get all segments.
        channel: str or int
            The channel to get data from. Can be '*' to get all channels.

        Returns
        -------
        patterns: list
            List of recursive patterns of len(orbits) that match the inputs.
        """
        return [self.__prepend_recursive_glob_pattern(f) for f in
                self.orbit_patterns(orbits, segment, channel)]

    @staticmethod
    def generic_glob_pattern(patterns):
        """ Create a generic glob search pattern from a list of patterns.

        Parameters
        ----------
        patterns: list
            Strings of patterns to search for.

        Returns
        -------
        glob_pattern: str
            The glob search pattern that accounts for the input patterns.
        """
        min_pattern = min([len(f) for f in patterns])
        split_patterns = [''.join([f[i] for f in patterns]) for i in
                          range(min_pattern)]
        return ''.join([f'[{f}]' for f in split_patterns])

    @staticmethod
    def __remove_recursive_glob_pattern(pattern):
        return pattern.replace('**', '*')

    @staticmethod
    def __prepend_recursive_glob_pattern(pattern):
        return f'**/{pattern}'


class GlobFiles:
    def __init__(self, path, pattern):
        self.__check_path_exists(path)
        self.__input_glob = list(Path(path).glob(pattern))
        self.__abs_paths = self.__get_absolute_paths_of_input_glob()
        self.__filenames = self.__get_filenames_of_input_glob()

    @staticmethod
    def __check_path_exists(path):
        try:
            if not os.path.exists(path):
                raise OSError(f'The path "{path}" does not exist on this '
                              'computer.')
        except TypeError:
            raise TypeError('The input value of path must be a string.')

    def __get_absolute_paths_of_input_glob(self):
        return sorted([str(f) for f in self.__input_glob if f.is_file()])

    def __get_filenames_of_input_glob(self):
        return sorted([f.name for f in self.__input_glob if f.is_file()])

    @property
    def abs_paths(self):
        return self.__abs_paths

    @property
    def filenames(self):
        return self.__filenames
