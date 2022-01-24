import math
from pathlib import Path
from pyuvs.data_files.filename import DataFilename


def make_orbit_code(orbit: int) -> str:
    """Make the 5 digit orbit "code" corresponding to the input orbit.

    Parameters
    ----------
    orbit: int
        The orbit number.

    Returns
    -------
    str
        The orbit code.

    Examples
    --------
    >>> from pyuvs.data_files import make_orbit_code
    >>> make_orbit_code(3453)
    '03453'

    """
    return f'{orbit}'.zfill(5)


def make_orbit_block(orbit: int) -> int:
    """Make the block number corresponding to the input orbit.

    Parameters
    ----------
    orbit: int
        The orbit number.

    Returns
    -------
    int
        The orbit block.

    Examples
    --------
    >>> from pyuvs.data_files import make_orbit_block
    >>> make_orbit_block(3453)
    3400

    """
    return math.floor(orbit / 100) * 100


def make_orbit_block_folder(orbit: int) -> str:
    """Make the name of the folder corresponding to the input orbit.

    This is the standard IUVS folder scheme, where orbits are organized into
    chunks of 100 orbits.

    Parameters
    ----------
    orbit: int
        The orbit number.

    Returns
    -------
    str
        The standard folder corresponding to the input orbit.

    Examples
    --------
    >>> from pyuvs.data_files import make_orbit_block_folder
    >>> make_orbit_block_folder(3453)
    'orbit03400'

    """
    block = make_orbit_block(orbit)
    code = make_orbit_code(block)
    return f'orbit{code}'


def make_filename_pattern(segment: str, orbit: int, channel: str) -> str:
    """Make the glob pattern of a set of IUVS filenames.

    Parameters
    ----------
    segment: str
        The orbital segment.
    orbit: int
        The orbit number.
    channel: str
        The instrument channel.

    Returns
    -------
    str
        The glob pattern of IUVS filenames.

    """
    return f'*{segment}*{orbit}*{channel}*.fits.gz'


def find_all_file_paths(data_directory: Path, segment: str, orbit: int,
                        channel: str) -> list[Path]:
    """Find all IUVS data file paths that match a set of patterns.

    Parameters
    ----------
    data_directory
        The absolute path to the directory where data files are located.
    segment: str
        The orbital segment.
    orbit: int
        The orbit number.
    channel: str
        The instrument channel.

    Returns
    -------
    list[Path]
        Sorted list of paths matching the input patterns.

    """
    data_filename_pattern = make_filename_pattern(segment, orbit, channel)
    return sorted(data_directory.glob(data_filename_pattern))


def find_outdated_file_paths(files: list[Path]) -> list[Path]:
    """Find the outdated files from a list of files.

    Parameters
    ----------
    files: list[Path]
        Collection of paths of IUVS data files.

    Returns
    -------
    list[Path]
        All of the outdated data file paths.

    """
    filenames = [str(f).replace('s0', 'a0') for f in files]
    last_time_stamp = ''
    last_channel = ''
    last_file = None
    old_files = []
    for f in filenames:
        df = DataFilename(f)
        if df.timestamp == last_time_stamp and df.channel == last_channel:
            old_files.append(Path(last_file))
        if 'a0' in f:
            f = f.replace('a0', 's0')
        last_time_stamp = df.timestamp
        last_channel = df.channel
        last_file = f
    return old_files


def find_latest_file_paths(data_directory: Path, segment: str, orbit: int,
                           channel: str) -> list[Path]:
    """Find the latest file paths that match a set of patterns.

    Parameters
    ----------
    data_directory: Path
        The directory where data files are located.
    segment: str
        The segment name.
    orbit: int
        The orbit number.
    channel: str
        The channel name.

    Returns
    -------
    list[Path]
        The latest file paths matching the input patterns.

    """
    all_files = find_all_file_paths(data_directory, segment, orbit, channel)
    outdated_files = find_outdated_file_paths(all_files)
    return [f for f in all_files if f not in outdated_files]


def find_latest_file_paths_from_block(data_directory: Path, segment: str,
                                      orbit: int, channel: str) -> list[Path]:
    """Find the latest file paths of a given pattern in a given directory,
    where the directory is divided into blocks of data spanning 100 orbits.

    Parameters
    ----------
    data_directory: Path
        The directory where the data blocks are located.
    segment: str
        The segment name.
    orbit: int
        The orbit number.
    channel: str
        The channel name.

    Returns
    ------
    list[Path]
        The latest file paths matching the input patterns.

    """
    block_path = data_directory / make_orbit_block_folder(orbit)
    return find_latest_file_paths(block_path, segment, orbit, channel)


def find_latest_apoapse_muv_file_paths_from_block(
        data_directory: Path, orbit: int) -> list[Path]:
    """Find the latest apoapse muv file paths in a given directory, where the
    directory is divided into blocks of data spanning 100 orbits.

    Parameters
    ----------
    data_directory: Path
        The directory where the data blocks are located.
    orbit: int
        The orbit number.

    Returns
    -------
    list[Path]
        The latest apoapse MUV file paths from the given orbit.

    """
    return find_latest_file_paths_from_block(
        data_directory, 'apoapse', orbit, 'muv')
