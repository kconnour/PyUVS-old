# Local imports
from maven_iuvs.files.files import SingleOrbitModeSequenceL1bFiles, L1bFiles


def single_orbit_segment(path, orbit, mode='muv', sequence='apoapse'):
    """ Make a SingleOrbitModeSequenceL1bFiles for files matching an input orbit, mode, and sequence.

    Parameters
    ----------
    path: str
        The location where to start looking for files.
    orbit: int
        The orbit to get files from
    mode: str
        The observing mode to get files from
    sequence: str
        The observing sequence to get files from

    Returns
    -------
    files: SingleOrbitModeSequenceL1bFiles:
        A SingleOrbitModeSequenceL1bFiles containing files from the requested orbit, mode, and sequence.
    """
    pattern = [f'**/*{sequence}-*{orbit}-*{mode}*']
    files = SingleOrbitModeSequenceL1bFiles(path, pattern)
    return files


def orbit_range_segment(path, orbit_start, orbit_end, mode='muv', sequence='apoapse'):
    """ Make an L1bFiles for all orbits between two endpoints.

    Parameters
    ----------
    path: str
        The location where to start looking for files.
    orbit_start: int
        The starting orbit to get files from.
    orbit_end: int
        The ending orbit to get files from.
    mode: str
        The observing mode. Can be '*' to get all modes. Default is 'muv'.
    sequence: str
        The observing sequence. Can be '*' to get all sequences. Default is 'apoapse'.

    Returns
    -------
    files: L1bFiles
        An L1bFiles of all files within the input orbital range.
    """

    orbits = []
    for orbit in range(orbit_start, orbit_end):
        orbits.append(str(orbit).zfill(5))

    patterns = []
    for counter, p in enumerate(range(len(orbits))):
        patterns.append(f'**/*{sequence}-*{orbits[counter]}-*{mode}*')

    files = L1bFiles(path, patterns)
    return files


def orbital_segment(path, orbits, mode='muv', sequence='apoapse'):
    """ Make an L1bFiles for an input list of orbits.

    Parameters
    ----------
    path: str
        The location where to start looking for files.
    orbits: list
        List of ints of orbits to get files from.
    mode: str
        The observing mode. Can be '*' to get all modes. Default is 'muv'.
    sequence: str
        The observing sequence. Can be '*' to get all sequences. Default is 'apoapse'.

    Returns
    -------
    files: L1bFiles
        An L1bFiles of all files within the input orbital range.
    """
    zfilled_orbits = []
    for orbit in orbits:
        zfilled_orbits.append(str(orbit).zfill(5))

    patterns = []
    for counter, p in enumerate(range(len(zfilled_orbits))):
        patterns.append(f'**/*{sequence}-*{zfilled_orbits[counter]}-*{mode}*')
    files = L1bFiles(path, patterns)
    return files
