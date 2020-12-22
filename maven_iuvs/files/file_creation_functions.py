# Local imports
from maven_iuvs.files.files import SingleOrbitModeSequenceL1bFiles


def single_orbit_segment(path, orbit, mode='muv', sequence='apoapse'):
    """ Make a SingleOrbitModeSequenceL1bFiles for files matching an input orbit, mode, and sequence

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
        A SingleOrbitModeSequenceL1bFiles containing files from the requested orbit, mode, and sequence
    """
    pattern = f'**/*{sequence}*{orbit}*{mode}*'
    files = SingleOrbitModeSequenceL1bFiles(path, pattern)
    return files


# TODO: make the function
def orbit_range_segment(path, orbit_start, orbit_end, mode='muv', sequence='apoapse'):
    # TODO: docstring
    pass


# TODO: make the function
def orbital_segment(path, orbits, mode='muv', sequence='apoapse'):
    # TODO: docstring
    pass
