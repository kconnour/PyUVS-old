# Built-in imports
import os

# 3rd-party imports
import numpy as np


# TODO: add try statements to these methods
class DataPath:
    """ A DataPath object creates absolute paths to where data reside, given a
     set of assumptions. """
    def make_orbit_block_paths(self, path, orbits):
        """ Make paths to orbits, assuming orbits are organized in blocks of
        100.

        Parameters
        ----------
        path: str
            The path where to begin looking for data.
        orbits: list
            List of ints of orbits.

        Returns
        -------
        paths: list
            The path (including orbit block) corresponding to each orbit.
        """
        return [self.__make_orbit_block_path(path, f) for f in orbits]

    def __make_orbit_block_path(self, path, orbit):
        return os.path.join(path, self.__make_orbit_block_folder(orbit))

    def __make_orbit_block_folder(self, orbit):
        return f'orbit{self.__round_to_nearest_hundred(orbit)}'

    @staticmethod
    def __round_to_nearest_hundred(orbit):
        return int(np.floor(int(orbit) / 100) * 100)

    # TODO: Data on the PDS are organized by year/month/<all data> so make a
    #  method for data organized that way


class PatternGlob:
    """ A PatternGlob object creates glob search patterns tailored to IUVS
    data. """
    def make_glob_pattern(self, orbit, sequence, channel):
        """ Make a glob pattern for an orbit, sequence, and channel.

        Parameters
        ----------
        orbit: str or int
            The orbit to get data from. Can be '*' to get all orbits.
        sequence: str or int
            The sequence to get data from. Can be '*' to get all sequences.
        channel: str or int
            The channel to get data from. Can be '*' to get all channels.

        Returns
        -------
        pattern: str
            The glob pattern that matches the input parameters.
        """
        pattern = f'*{sequence}-*{self.__orbit_to_string(orbit)}-{channel}*'
        return self.__remove_recursive_glob_pattern(pattern)

    @staticmethod
    def __orbit_to_string(orbit):
        return str(orbit).zfill(5)

    @staticmethod
    def __remove_recursive_glob_pattern(pattern):
        return pattern.replace('**', '*')

    def make_recursive_glob_pattern(self, orbit, sequence, channel):
        """ Make a recursive glob pattern for an orbit, sequence, and channel.

        Parameters
        ----------
        orbit: str or int
            The orbit to get data from. Can be '*' to get all orbits.
        sequence: str or int
            The sequence to get data from. Can be '*' to get all sequences.
        channel: str or int
            The channel to get data from. Can be '*' to get all channels.

        Returns
        -------
        pattern: str
            The recursive glob pattern that matches the input parameters.
        """
        pattern = self.make_glob_pattern(orbit, sequence, channel)
        return self.__prepend_recursive_glob_pattern(pattern)

    @staticmethod
    def __prepend_recursive_glob_pattern(pattern):
        return f'**/{pattern}'

    def make_patterns_from_orbits(self, orbits, sequence, channel):
        """ Make glob patterns for each orbit in a list of orbits.

        Parameters
        ----------
        orbits: list
            List of ints or strings of orbits to make patterns for.
        sequence: str or int
            The sequence to get data from. Can be '*' to get all sequences.
        channel: str or int
            The channel to get data from. Can be '*' to get all channels.

        Returns
        -------
        patterns: list
            List of patterns of len(orbits) that match the inputs.
        """
        converted_orbits = [self.__orbit_to_string(orbit) for orbit in orbits]
        return [self.make_glob_pattern(orbit, sequence, channel) for orbit in
                converted_orbits]

    def make_recursive_patterns_from_orbits(self, orbits, sequence, channel):
        """ Make recursive glob patterns for each orbit in a list of orbits.

        Parameters
        ----------
        orbits: list
            List of ints or strings of orbits to make patterns for.
        sequence: str or int
            The sequence to get data from. Can be '*' to get all sequences.
        channel: str or int
            The channel to get data from. Can be '*' to get all channels.

        Returns
        -------
        patterns: list
            List of recursive patterns of len(orbits) that match the inputs.
        """
        return [self.__prepend_recursive_glob_pattern(f) for f in
                self.make_patterns_from_orbits(orbits, sequence, channel)]
