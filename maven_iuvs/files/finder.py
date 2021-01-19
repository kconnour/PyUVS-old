# Built-in imports
import os
from pathlib import Path

# 3rd-party imports
import numpy as np

# Local imports
from maven_iuvs.misc import orbit_to_string


class DataPath:
    """ A DataPath object creates absolute paths to where data products reside,
    given a set of assumptions. """
    def block_path(self, path: str, orbit: int) -> str:
        """ Make the path to an orbit, assuming orbits are organized in blocks
        of 100 orbits.

        Parameters
        ----------
        path: str
            Absolute path of the IUVS data root location (where data are
            organized into blocks).
        orbit: int
            The orbit number.

        Returns
        -------
        path: str
            The path with orbit block appended corresponding to the input
            orbit.

        Examples
        --------
        >>> DataPath().block_path('/foo/bar', 7777)
        /foo/bar/orbit07700
        """
        return os.path.join(path, self.__make_orbit_block_folder_name(orbit))

    def orbit_block_paths(self, path: str, orbits: list[int]) -> list[str]:
        """ Make paths to orbits, assuming orbits are organized in blocks of
        100 orbits.

        Parameters
        ----------
        path: str
            Absolute path of the IUVS data root location (where data are
            organized into blocks).
        orbits: list[int]
            The orbit numbers.

        Returns
        -------
        paths: list[str]
            The path with orbit block appended corresponding to the input
            orbits.

        Examples
        --------
        >>> DataPath().orbit_block_paths('/foo/bar', [3495, 3500, 3505]
        ['/foo/bar/orbit03400', '/foo/bar/orbit03500', '/foo/bar/orbit03500']
        """
        return [self.block_path(path, f) for f in orbits]

    def __make_orbit_block_folder_name(self, orbit: int) -> str:
        rounded_orbit = self.__round_to_nearest_hundred(orbit)
        return f'orbit{orbit_to_string(rounded_orbit)}'

    @staticmethod
    def __round_to_nearest_hundred(orbit: int) -> int:
        return int(np.floor(orbit / 100) * 100)


class DataPattern:
    """ A DataPattern object creates glob search patterns tailored to IUVS
    data. """
    def pattern(self, orbit: str, segment: str, channel: str,
                extension: str = 'fits') -> str:
        """ Make a glob pattern for an input orbit, segment, channel, and
        (optionally) extension pattern.

        Parameters
        ----------
        orbit: str
            The orbit pattern to get data from.
        segment: str
            The segment pattern to get data from.
        channel: str
            The channel pattern to get data from.
        extension: str
            The file extension pattern to get data from. Default is 'fits'.

        Returns
        -------
        pattern: str
            The glob pattern that matches the input patterns.

        Examples
        --------
        >>> DataPattern().pattern('*', 'periapse', 'fuv')
        *periapse-*-fuv*.fits*

        >>> d = DataPattern()
        >>> segment_pattern = d.generic_pattern(['apoapse', 'inlimb'])
        >>> channel_pattern = d.generic_pattern(['fuv', 'ech'])
        >>> d.pattern('*9984', segment_pattern, channel_pattern)
        *[ai][pn][ol][ai][pm][sb]*-*9984-[fe][uc][vh]*.fits*
        """
        pattern = f'*{segment}-{orbit}-{channel}*.{extension}*'
        return self.__remove_recursive_glob_pattern(pattern)

    def single_orbit_pattern(self, orbit: int, segment: str, channel: str,
                             extension: str = 'fits') -> str:
        """ Make a glob pattern for an input orbit number, as well as segment,
        channel, and (optionally) extension pattern.

        Parameters
        ----------
        orbit: int
            The orbit number to get data from.
        segment: str
            The segment pattern to get data from.
        channel: str
            The channel pattern to get data from.
        extension: str
            The file extension pattern to get data from. Default is 'fits'.

        Returns
        -------
        pattern: str
            The glob pattern that matches the input patterns.

        Examples
        --------
        >>> DataPattern().single_orbit_pattern(9801, 'periapse', 'fuv')
        *periapse-orbit09801-fuv*.fits*
        """
        orb_pattern = f'orbit{orbit_to_string(orbit)}'
        return self.pattern(orb_pattern, segment, channel, extension=extension)

    def orbit_patterns(self, orbits: list[int], segment: str, channel: str,
                       extension: str = 'fits') -> list[str]:
        """ Make glob patterns for each orbit in a list of orbits.

        Parameters
        ----------
        orbits: list[int]
            Orbits to make patterns for.
        segment: str
            The segment pattern to get data from.
        channel: str or int
            The channel pattern to get data from.
        extension: str
            The file extension pattern to get data from. Default is 'fits'.

        Returns
        -------
        patterns: list[str]
            Patterns for each input orbit.

        Examples
        --------
        >>> DataPattern().orbit_patterns([3453, 3455], 'apoapse', 'muv')
        ['*apoapse-orbit03453-muv*.fits*', '*apoapse-orbit03455-muv*.fits*']
        """
        return [self.single_orbit_pattern(f, segment, channel,
                                          extension=extension) for f in orbits]

    @staticmethod
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
        *[ai][pn][ol][ai][pm][sb]*
        """
        shortest_pattern_length = min([len(f) for f in patterns])
        split_patterns = (''.join([f[i] for f in patterns]) for i in
                          range(shortest_pattern_length))
        pattern = ''.join([f'[{f}]' for f in split_patterns])
        return '*' + pattern + '*'

    @staticmethod
    def prepend_recursive_glob_pattern(pattern: str) -> str:
        """ Prepend '**/' to the input pattern.

        Parameters
        ----------
        pattern: str
            Generic glob pattern.

        Returns
        -------
        pattern: str
            Input pattern with '**/' prepended.
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

    def perform_glob():
        return Path(path).glob(pattern)

    # TODO: I dunno how to tell the code that inp_glob is a generator without
    #  hackish solutions
    def get_absolute_paths_of_glob(inp_glob) -> list[str]:
        return sorted([str(f) for f in inp_glob if f.is_file()])

    check_path_exists()
    g = perform_glob()
    return get_absolute_paths_of_glob(g)
