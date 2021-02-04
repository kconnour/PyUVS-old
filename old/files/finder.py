# Built-in imports
import os
from pathlib import Path
from typing import Any, Generator, Iterable

# Local imports
from old.files import IUVSDataFilenameCollection


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
