# Built-in imports
import os

# 3rd-party imports
import numpy as np

# Local imports
from maven_iuvs.files.files import SingleOrbitSequenceChannelL1bFiles, L1bFiles


# TODO: move these to another file
# TODO: add try statements to these methods
class IUVSGlobs:
    """ A GlobPattern object creates glob search patterns tailored to IUVS
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

    def make_orbit_path(self, path, orbit):
        """ Make the path to orbits, assuming orbits are organized in blocks.

        Parameters
        ----------
        path: str
            The path where to begin looking for data.
        orbit: int
            The orbit.

        Returns
        -------
        paths: list
            The path (including orbit block) corresponding to orbit.
        """
        return os.path.join(path, self.__make_orbit_block_folder(orbit))

    def make_orbit_paths(self, path, orbits):
        return [self.make_orbit_path(path, f) for f in orbits]

    @staticmethod
    def __round_to_nearest_hundred(orbit):
        return int(np.floor(int(orbit)/100) * 100)

    def __make_orbit_block_folder(self, orbit):
        return f'orbit{self.__round_to_nearest_hundred(orbit)}'


def segment(path, orbit, sequence='apoapse', channel='muv'):
    """ Make a SingleOrbitSequenceChannelL1bFiles for files matching an input
    orbit, sequence, and channel.

    Parameters
    ----------
    path: str
        The location where to start looking for files.
    orbit: int
        The orbit to get files from.
    sequence: str
        The observing sequence to get files from.
    channel: str
        The observing mode to get files from.

    Returns
    -------
    files: SingleOrbitSequenceChannelL1bFiles:
        A SingleOrbitSequenceChannelL1bFiles containing files from the
        requested orbit, sequence, and channel.
    """
    pattern = IUVSGlobs().make_recursive_glob_pattern(orbit, sequence, channel)
    return SingleOrbitSequenceChannelL1bFiles(path, pattern)


def multi_segments(path, orbits, sequence='apoapse', channel='muv'):
    """ Make an L1bFiles for an input list of orbits.

    Parameters
    ----------
    path: str
        The location where to start looking for files.
    orbits: list
        List of ints of orbits to get files from.
    sequence: str
        The observing sequence. Can be '*'. Default is 'apoapse'.
    channel: str
        The observing channel. Can be '*'. Default is 'muv'.

    Returns
    -------
    files: list
        An L1bFiles of all files at the input orbits.
    """
    paths = IUVSGlobs().make_orbit_paths(path, orbits)
    patterns = IUVSGlobs().make_recursive_patterns_from_orbits(orbits,
                                                               sequence,
                                                               channel)

    single_orbit_files = []
    for i in range(len(paths)):
        try:
            file = L1bFiles(paths[i], patterns[i])
            single_orbit_files.append(file)
        except ValueError:
            continue

    return combine_multiple_l1b_files(single_orbit_files)


def segment_range(path, orbit_start, orbit_end, sequence='apoapse',
                  channel='muv'):
    """ Make an L1bFiles for all orbits between two endpoints.

    Parameters
    ----------
    path: str
        The location where to start looking for files.
    orbit_start: int
        The starting orbit to get files from.
    orbit_end: int
        The ending orbit to get files from.
    sequence: str
        The observing sequence. Can be '*'. Default is 'apoapse'.
    channel: str
        The observing channel. Can be '*'. Default is 'muv'.

    Returns
    -------
    files: L1bFiles
        An L1bFiles of all files within the input orbital range.
    """
    orbits = list(range(orbit_start, orbit_end))
    return multi_segments(path, orbits, sequence=sequence, channel=channel)


# TODO: This should be a method in Files
def combine_multiple_l1b_files(l1b_files):
    for counter, files in enumerate(l1b_files):
        if counter == 0:
            continue
        for f in range(len(files.filenames)):
            l1b_files[0].filenames.append(files.filenames[f])
            l1b_files[0].absolute_paths.append(files.absolute_paths[f])
    return l1b_files[0]
