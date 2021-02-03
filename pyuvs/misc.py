"""misc.py holds miscellaneous utilities. These are all subject to change.
"""
import os


def get_project_path() -> str:
    """ et the absolute path of the project.

    Returns
    -------
    str
        Absolute path of the project.

    """
    return os.path.abspath(os.path.join(os.path.dirname(
        os.path.realpath(__file__)), '..'))


def orbit_code(orbit: int) -> str:
    """Make the "code" for an input orbit.

    Parameters
    ----------
    orbit: int
        The orbit number.

    Returns
    -------
    str
        The orbit code.

    """
    if not isinstance(orbit, int):
        raise TypeError('orbit must be an int.')
    return str(orbit).zfill(5)
