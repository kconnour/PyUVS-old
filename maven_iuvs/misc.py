def orbit_to_string(orbit):
    """ Turn an orbit into a 5 digit string representation.

    Parameters
    ----------
    orbit: int
        The orbit to convert.

    Returns
    -------
    orbit: str
        5 digit string of the orbit
    """
    return str(orbit).zfill(5)
