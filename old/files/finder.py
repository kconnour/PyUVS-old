# Built-in imports
import os
from pathlib import Path
from typing import Any, Generator, Iterable

# 3rd-party imports
import numpy as np

# Local imports
from pyuvs.misc.orbit_code import orbit_code
from old.files import IUVSDataFilenameCollection


class DataPath:
    """ A DataPath object creates absolute paths to where data products reside,
    given a set of assumptions. """
    def __init__(self, path: str) -> None:
        """
        Parameters
        ----------
        path: str
            Absolute path of the IUVS data root location.
        """
        self.__raise_type_error_if_input_is_not_string(path)
        self.__path = path

    @staticmethod
    def __raise_type_error_if_input_is_not_string(path: Any) -> None:
        if not isinstance(path, str):
            raise TypeError('The input to DataPath must be a str.')

    def block(self, orbit: int) -> str:
        """ Make the path to an orbit, assuming orbits are organized in blocks
        of 100 orbits.

        Parameters
        ----------
        orbit: int
            The orbit number.

        Returns
        -------
        path: str
            The path with orbit block appended corresponding to the input
            orbit.

        Examples
        --------
        >>> path = DataPath('/foo/bar/')
        >>> path.block(7777)
        '/foo/bar/orbit07700'
        """
        try:
            return os.path.join(self.__path, self.__block_folder_name(orbit))
        except TypeError:
            raise TypeError('Input should be a int.')

    def block_paths(self, orbits: Iterable[int]) -> list[str]:
        """ Make paths to a series of orbits, assuming orbits are organized in
        blocks of 100 orbits.

        Parameters
        ----------
        orbits: Iterable[int]
            The orbit numbers.

        Returns
        -------
        paths: list[str]
            The path with orbit block appended corresponding to the input
            orbits.

        Examples
        --------
        >>> path = DataPath('/foo/bar/')
        >>> path.block_paths([3495, 3500, 3505])
        ['/foo/bar/orbit03400', '/foo/bar/orbit03500', '/foo/bar/orbit03500']
        """
        try:
            return [self.block(f) for f in orbits]
        except TypeError:
            raise TypeError('Each value in orbits should be an int.')

    def __block_folder_name(self, orbit: int) -> str:
        orbit_block = self.__orbit_block(orbit)
        return f'orbit{orbit_code(orbit_block)}'

    @staticmethod
    def __orbit_block(orbit: int) -> int:
        return int(np.floor(orbit / 100) * 100)


class DataPattern:
    """ A DataPattern object creates glob search patterns tailored to IUVS
    data. """
    def data_pattern(self, level: str = '*', segment: str = '*',
                     orbit: str = '*', channel: str = '*',
                     timestamp: str = '*', version: str = '*',
                     extension: str = 'fits') -> str:
        """ Make a generic pattern tailored to IUVS data.

        Parameters
        ----------
        level: str, optional
            The level pattern to get data from. Default is '*'.
        segment: str, optional
            The segment pattern to get data from. Default is '*'.
        orbit: str, optional
            The orbit pattern to get data from. Default is '*'.
        channel: str, optional
            The channel pattern to get data from. Default is '*'.
        timestamp: str, optional
            The timestamp pattern to get data from. Default is '*'.
        version: str, optional
            The version pattern to get data from. Default is '*'.
        extension: str, optional
            The extension pattern to get data from. Default is 'fits'.

        Returns
        -------
        pattern: str
            The pattern with the input sub-patterns.

        Examples
        --------
        >>> dp = DataPattern()
        >>> dp.data_pattern()
        'mvn_iuv_*_*-orbit*-*_*T*_*_*.fits*'

        >>> dp.data_pattern(segment='apoapse', channel='ech')
        'mvn_iuv_*_apoapse-orbit*-ech_*T*_*_*.fits*'
        """
        pattern = f'mvn_iuv_{level}_{segment}-orbit{orbit}-{channel}_' \
                  f'{timestamp}T*_{version}_*.{extension}*'
        return self.__remove_recursive_glob_pattern(pattern)

    def orbit_pattern(self, orbit: int, segment: str, channel: str) -> str:
        """ Make a glob pattern for an input orbit number, as well as segment
        and channel patterns.

        Parameters
        ----------
        orbit: int
            The orbit number to get data from.
        segment: str
            The segment pattern to get data from.
        channel: str
            The channel pattern to get data from.

        Returns
        -------
        pattern: str
            The glob pattern that matches the input patterns.

        Examples
        --------
        >>> dp = DataPattern()
        >>> dp.orbit_pattern(9000, 'inlimb', 'muv')
        'mvn_iuv_*_inlimb-orbit09000-muv_*T*_*_*.fits*'

        >>> segment_pattern = dp.generic_pattern(['apoapse', 'inlimb'])
        >>> channel_pattern = dp.generic_pattern(['fuv', 'ech'])
        >>> dp.orbit_pattern(9984, segment_pattern, channel_pattern)
        'mvn_iuv_*_*[ai][pn][ol][ai][pm][sb]*-orbit09984-*[fe][uc][vh]*_*T*_*_*.fits*'
        """
        try:
            return self.data_pattern(orbit=orbit_code(orbit), segment=segment,
                                     channel=channel)
        except TypeError:
            raise TypeError('orbit should be an int.')
        except ValueError:
            raise ValueError('orbit should be an int.')

    def multi_orbit_patterns(self, orbits: Iterable[int], segment: str,
                             channel: str) -> list[str]:
        """ Make glob patterns for each orbit in a list of orbits.

        Parameters
        ----------
        orbits: Iterable[int]
            Orbits to make patterns for.
        segment: str
            The segment pattern to get data from.
        channel: str or int
            The channel pattern to get data from.

        Returns
        -------
        patterns: list[str]
            Patterns for each input orbit.

        Examples
        --------
        >>> DataPattern().multi_orbit_patterns([3453, 3455], 'apoapse', 'muv')
        ['mvn_iuv_*_apoapse-orbit03453-muv_*T*_*_*.fits*', 'mvn_iuv_*_apoapse-orbit03455-muv_*T*_*_*.fits*']
        """
        try:
            return [self.orbit_pattern(f, segment, channel) for f in orbits]
        except TypeError:
            raise TypeError('The input value of orbit should be an iterable.')
        except ValueError:
            raise ValueError('Each value in orbits should be an int.')

    @staticmethod
    # TODO: Technically, patterns can be any Iterable except a generator but I
    #  don't know how to fix my code so that it can take any iterable.
    def generic_pattern(patterns: list[str]) -> str:
        """ Create a generic glob search pattern from a list of patterns. This
        replicates the functionality of the brace expansion glob has in some
        shells.

        Parameters
        ----------
        patterns: list[str]
            Patterns to search for.

        Returns
        -------
        glob_pattern: str
            The glob search pattern that accounts for the input patterns.

        Examples
        --------
        >>> segments = ['apoapse', 'inlimb']
        >>> DataPattern().generic_pattern(segments)
        '*[ai][pn][ol][ai][pm][sb]*'
        """
        try:
            shortest_pattern_length = min([len(f) for f in patterns])
            split_patterns = (''.join([f[i] for f in patterns]) for i in
                              range(shortest_pattern_length))
            pattern = ''.join([f'[{f}]' for f in split_patterns])
            return '*' + pattern + '*'
        except TypeError:
            raise TypeError('patterns must be an iterable.')

    @staticmethod
    def prepend_recursive_pattern(pattern: str) -> str:
        """ Prepend '**/' to the input pattern.

        Parameters
        ----------
        pattern: str
            Generic glob pattern.

        Returns
        -------
        pattern: str
            Input pattern with '**/' prepended.

        Examples
        --------
        >>> dp = DataPattern()
        >>> dp.prepend_recursive_pattern(dp.data_pattern())
        '**/mvn_iuv_*_*-orbit*-*_*T*_*_*.fits*'
        """
        return f'**/{pattern}'

    @staticmethod
    def __remove_recursive_glob_pattern(pattern: str) -> str:
        return pattern.replace('**', '*')


def glob_files(path: str, pattern: str) -> list[str]:
    """ Glob all the files matching a glob pattern in a path.

    Parameters
    ----------
    path: str
        Path where look for data.
    pattern: str
        Pattern to glob for. Can be recursive.

    Returns
    -------
    files: list[str]
        Absolute paths of files matching pattern in path.
    """
    def check_path_exists() -> None:
        try:
            if not os.path.exists(path):
                raise OSError(f'The path "{path}" does not exist on this '
                              'computer.')
        except TypeError:
            raise TypeError('The input value of path must be a string.')

    def perform_glob() -> Generator:
        return Path(path).glob(pattern)

    def get_absolute_paths_of_glob(inp_glob: Generator) -> list[str]:
        return sorted([str(f) for f in inp_glob if f.is_file()])

    check_path_exists()
    g = perform_glob()
    return get_absolute_paths_of_glob(g)


def soschob(path: str, orbit: int, segment: str = 'apoapse',
            channel: str = 'muv') -> IUVSDataFilenameCollection:
    """ Make an IUVSDataFilenameCollection for files matching an input orbit,
    segment pattern, and channel pattern, assuming orbits are organized in
    blocks of 100.

    Parameters
    ----------
    path: str
        The location the IUVS data.
    orbit: int
        The orbit to get files from.
    segment: str
        The observing segment to get files from. Default is 'apoapse'.
    channel: str
        The observing mode to get files from. Default is 'muv'.

    Returns
    -------
    files: IUVSDataFilenameCollection:
        Matching files from the input orbit, segment, and channel.
    """
    p = DataPath(path).block(orbit)
    pat = DataPattern().orbit_pattern(orbit, segment, channel)
    abs_paths = glob_files(p, pat)
    return IUVSDataFilenameCollection(abs_paths)


def multi_orbit_files(path: str, orbits: list[int], segment: str = 'apoapse',
                      channel: str = 'muv') -> IUVSDataFilenameCollection:
    """ Make an IUVSDataFilenameCollection for an input list of orbits,
    segment pattern, and channel pattern, assuming orbits are organized in
    blocks of 100.

    Parameters
    ----------
    path: str
        The location where to start looking for files.
    orbits: list[int]
        Orbits to get files from.
    segment: str
        The observing segment to get files from. Default is 'apoapse'.
    channel: str
        The observing channel to get files from. Default is 'muv'.

    Returns
    -------
    files: IUVSDataFilenameCollection
        Matching files from the input orbits, segment, and channel.
    """
    p = DataPath(path).block_paths(orbits)
    pat = DataPattern().multi_orbit_patterns(orbits, segment, channel)
    path_list = [glob_files(p[f], pat[f]) for f in range(len(p))]
    abs_paths = [k for f in path_list for k in f]
    return IUVSDataFilenameCollection(abs_paths)


def orbit_range_files(path: str, orbit_start: int, orbit_end: int,
                      segment: str = 'apoapse', channel: str = 'muv') \
        -> IUVSDataFilenameCollection:
    """ Make an IUVSDataFilenameCollection for all orbits in a range of orbits
    with a segment pattern and channel pattern, assuming orbits are organized
    in blocks of 100.

    Parameters
    ----------
    path: str
        The location where to start looking for files.
    orbit_start: int
        The starting orbit to get files from.
    orbit_end: int
        The ending orbit to get files from.
    segment: str
        The observing segment to get files from. Default is 'apoapse'.
    channel: str
        The observing channel to get files from. Default is 'muv'.

    Returns
    -------
    files: IUVSDataFilenameCollection
        Matching files from the input orbit range, segment, and channel.
    """
    orbits = list(range(orbit_start, orbit_end))
    return multi_orbit_files(path, orbits, segment=segment, channel=channel)
