"""This module provides functions to work with IUVS data swaths.
"""
import numpy as np


def swath_number(mirror_angles: np.ndarray) -> np.ndarray:
    """Make the swath number associated with each mirror angle.

    This function assumes the input is all the mirror angles (or, equivalently,
    the field of view) from an orbital segment. Omitting some mirror angles
    may result in nonsensical results. Adding additional mirror angles from
    multiple segments or orbits will certainly result in nonsensical results.

    Parameters
    ----------
    mirror_angles: np.ndarray
        1D array of the mirror angles from an orbital segment.

    Returns
    -------
    np.ndarray
        The swath number associated with each mirror angle.

    Notes
    -----
    This algorithm assumes the mirror in roughly constant step sizes except
    when making a swath jump. It finds the median step size and then uses
    this number to find swath discontinuities. It interpolates between these
    indices and takes the floor of these values to get the integer swath
    number.

    Examples
    --------
    Get the swath number from a set of test mirror angles.

    >>> import pyuvs as pu
    >>> mirror_angles = np.array([40, 45, 50, 35, 40, 45, 50])
    >>> pu.swath_number(mirror_angles)
    array([0, 0, 0, 1, 1, 1, 1])

    Get the number of integrations in swath 1, where there are an unequal
    number of integrations in each swath.

    >>> import pyuvs as pu
    >>> mirror_angles = np.concatenate([np.linspace(35, 40, num=50),
    ...                                 np.linspace(32, 42, num=100),
    ...                                 np.linspace(33, 53, num=200)])
    >>> sn = pu.swath_number(mirror_angles)
    >>> np.sum(sn==1)
    100

    """
    mirror_change = np.diff(mirror_angles)
    threshold = np.abs(np.median(mirror_change)) * 2
    mirror_discontinuities = np.where(np.abs(mirror_change) > threshold)[0] + 1
    if any(mirror_discontinuities):
        n_swaths = len(mirror_discontinuities) + 1
        integrations = range(len(mirror_angles))
        interp_swaths = np.interp(integrations, mirror_discontinuities,
                                  range(1, n_swaths), left=0)
        return np.floor(interp_swaths).astype('int')
    else:
        return np.zeros(mirror_angles.shape)
