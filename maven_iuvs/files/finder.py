# Built-in imports
import os
from pathlib import Path

# 3rd-party imports
import numpy as np

# Local imports
from maven_iuvs.misc import orbit_to_string


class DataPath:
    """ A DataPath object creates absolute paths to where data reside, given a
     set of assumptions. """
    def block_path(self, path, orbit):
        """ Make the path to an orbit, assuming orbits are organized in blocks
        of 100 orbits.

        Parameters
        ----------
        path: str
            Absolute path of the IUVS data root location (where data are
            organized into blocks.)
        orbit: int
            The orbit number.

        Returns
        -------
        path: str
            The path with orbit block appended corresponding to the input
            orbit.
        """
        return os.path.join(path, self.__make_orbit_block_folder_name(orbit))

    def orbit_block_paths(self, path, orbits):
        """ Make paths to orbits, assuming orbits are organized in blocks of
        100 orbits.

        Parameters
        ----------
        path: str
            Absolute path of the IUVS data root location (where data are
            organized into blocks.)
        orbits: list
            Ints of orbit numbers.

        Returns
        -------
        paths: list
            The path with orbit block appended corresponding to the input
            orbits.
        """
        return [self.block_path(path, f) for f in orbits]

    def __make_orbit_block_folder_name(self, orbit):
        rounded_orbit = self.__round_to_nearest_hundred(orbit)
        return f'orbit{orbit_to_string(rounded_orbit)}'

    @staticmethod
    def __round_to_nearest_hundred(orbit):
        return int(np.floor(orbit / 100) * 100)


class DataPattern:
    """ A DataPattern object creates glob search patterns tailored to IUVS
    data. """
    def pattern(self, orbit, segment, channel, extension='fits'):
        """ Make a glob pattern for an input orbit, segment, and channel.

        Parameters
        ----------
        orbit: str
            The orbit pattern to get data from.
        segment: str
            The segment pattern to get data from.
        channel: str or int
            The channel pattern to get data from.
        extension: str
            The file extension pattern to get data from. Default is 'fits'.

        Returns
        -------
        pattern: str
            The glob pattern that matches the input patterns.
        """
        pattern = f'*{segment}-{orbit}-{channel}*.{extension}*'
        return self.__remove_recursive_glob_pattern(pattern)

    def recursive_pattern(self, orbit, segment, channel, extension='fits'):
        """ Make a recursive glob pattern for an orbit, segment, and channel.

        Parameters
        ----------
        orbit: str
            The orbit pattern to get data from.
        segment: str
            The segment pattern to get data from.
        channel: str or int
            The channel pattern to get data from.
        extension: str
            The file extension pattern to get data from. Default is 'fits'.

        Returns
        -------
        pattern: str
            The recursive glob pattern that matches the input patterns.
        """
        pattern = self.pattern(orbit, segment, channel, extension=extension)
        return self.__prepend_recursive_glob_pattern(pattern)

    def orbit_patterns(self, orbits, segment, channel, extension='fits'):
        """ Make glob patterns for each orbit in a list of orbits.

        Parameters
        ----------
        orbits: list
            List of ints or strings of orbits to make patterns for.
        segment: str
            The segment pattern to get data from.
        channel: str or int
            The channel pattern to get data from.
        extension: str
            The file extension pattern to get data from. Default is 'fits'.

        Returns
        -------
        patterns: list
            Patterns of len(orbits) that match the inputs.
        """
        orbit_patterns = [orbit_to_string(f) for f in orbits]
        return [self.pattern(f, segment, channel, extension=extension)
                for f in orbit_patterns]

    def recursive_orbit_patterns(self, orbits, segment, channel,
                                 extension='fits'):
        """ Make recursive glob patterns for each orbit in a list of orbits.

        Parameters
        ----------
        orbits: list
            List of ints or strings of orbits to make patterns for.
        segment: str
            The segment pattern to get data from.
        channel: str or int
            The channel pattern to get data from.
        extension: str
            The file extension pattern to get data from. Default is 'fits'.

        Returns
        -------
        patterns: list
            List of recursive patterns of len(orbits) that match the inputs.
        """
        return [self.__prepend_recursive_glob_pattern(f) for f in
                self.orbit_patterns(orbits, segment, channel,
                                    extension=extension)]

    @staticmethod
    def generic_pattern(patterns):
        """ Create a generic glob search pattern from a list of patterns. This
        replicates the functionality of the brace expansion glob has in some
        shells.

        Parameters
        ----------
        patterns: list
            Strings of patterns to search for.

        Returns
        -------
        glob_pattern: str
            The glob search pattern that accounts for the input patterns.

        Examples
        --------
        >>> segments = ['apoapse', 'inlimb']
        >>> DataPattern().generic_pattern(segments)
        [ai][pn][ol][ai][pm][sb]
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


class FileGlob:
    """ A FileGlob performs globbing of files and stores their absolute paths
    and their filenames. """
    def __init__(self, path, pattern):
        """
        Parameters
        ----------
        path: str
            The absolute path where to begin looking for files.
        pattern: str
            The pattern to search for. Can include '**' for recursive globbing.
        """
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
        """ Get the absolute paths of the globbed files.

        Returns
        -------
        absolute_paths: list
            Absolute paths of all globbed files.
        """
        return self.__abs_paths

    @property
    def filenames(self):
        """ Get the filenames of the globbed files.

        Returns
        -------
        filenames: list
            Filenames of all globbed files.
        """
        return self.__filenames

    # TODO: It seems a number of methods in IUVSDataFiles could also go here.
    #  Think of some clever way to combine them
