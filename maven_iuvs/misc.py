

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
    return str(orbit).zfill(5)
