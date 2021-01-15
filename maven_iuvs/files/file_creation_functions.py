# Local imports
from maven_iuvs.files.finder import DataPath, DataPattern, FileGlob
from maven_iuvs.files.files import L1bDataFiles, SingleSoschobL1bDataFiles


def soschob(path, orbit, segment='apoapse', channel='muv'):
    """ Make a SingleSoschobL1bDataFiles for files matching an input orbit,
    segment pattern, and channel pattern, assuming orbits are organized in
    blocks of 100.

    Parameters
    ----------
    path: str
        The location the IUVS data.
    orbit: int
        The orbit to get files from.
    segment: str
        The observing segment to get files from.
    channel: str
        The observing mode to get files from.

    Returns
    -------
    files: SingleSoschobL1bDataFiles:
        A SingleSoschobL1bDataFiles containing files from the
        requested orbit, segment, and channel.
    """
    p = DataPath().block_path(path, orbit)
    pat = DataPattern().pattern(orbit, segment, channel)
    abs_paths = FileGlob(p, pat).abs_paths
    return SingleSoschobL1bDataFiles(abs_paths)


def multi_orbit_files(path, orbits, segment='apoapse', channel='muv'):
    """ Make an L1bDataFiles for an input list of orbits, segment pattern, and
    channel pattern, assuming orbits are organized in blocks of 100.

    Parameters
    ----------
    path: str
        The location where to start looking for files.
    orbits: list
        List of ints of orbits to get files from.
    segment: str
        The observing segment to get files from. Default is 'apoapse'.
    channel: str
        The observing channel to get files from. Default is 'muv'.

    Returns
    -------
    files: list
        An L1bFiles of all files from the input orbits.
    """
    p = DataPath().orbit_block_paths(path, orbits)
    pat = DataPattern().orbit_patterns(orbits, segment, channel)
    path_list = [FileGlob(p[f], pat[f]).abs_paths for f in range(len(p))]
    abs_paths = [k for f in path_list for k in f]
    return L1bDataFiles(abs_paths)


def orbit_range_files(path, orbit_start, orbit_end, segment='apoapse',
                      channel='muv'):
    """ Make an L1bDataFiles for all orbits in a range of orbits with a segment
    pattern and channel pattern, assuming orbits are organized in blocks of
    100.

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
    files: L1bFiles
        An L1bFiles of all files within the input orbital range.
    """
    orbits = list(range(orbit_start, orbit_end))
    return multi_orbit_files(path, orbits, segment=segment, channel=channel)
