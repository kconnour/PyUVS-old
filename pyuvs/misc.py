import os


def get_project_path() -> str:
    """ Get the absolute path of the project.

    Returns
    -------
    path: str
        Absolute path of the project.
    """
    return os.path.abspath(os.path.join(os.path.dirname(
        os.path.realpath(__file__)), '../..'))


def orbit_code(orbit: int) -> str:
    """ Get the "code" for an input orbit.

    Parameters
    ----------
    orbit: int
        The orbit number.

    Returns
    -------
    code: str
        The orbit code.
    """
    try:
        return str(int(orbit)).zfill(5)
    except TypeError:
        raise TypeError('The input should be an int')
    except ValueError:
        raise ValueError('The input should be an int.')
