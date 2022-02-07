"""This module provides functions to work with swaths.
"""
import numpy as np


def swath_number(mirror_angles: np.ndarray) -> np.ndarray:
    """Get the swath number associated with each integration.

    Parameters
    ----------
    mirror_angles: np.ndarray
        1D array of the mirror angles from an orbital segment.

    Returns
    -------
    np.ndarray
        Swath number associated with each mirror angle.

    Notes
    -----
    This algorithm gets the angular difference between swaths. The mirror does
    not always move in equal step sizes, so this finds the indices where the
    jumps occur. To turn these into swath numbers, it interpolates between the
    indices (for instance, indices 412 to 920 are all 1.x because they all
    belong to swath 1). Then take the floor of these to get the integer swath
    number.

    """
    mirror_diff = np.diff(mirror_angles)
    threshhold = np.abs(mirror_diff[0] * 2)
    mirror_discontinuities = np.where(np.abs(mirror_diff) > threshhold)[0] + 1
    n_swaths = len(mirror_discontinuities) + 1
    interp_swaths = np.interp(range(len(mirror_angles)), mirror_discontinuities,
                              range(1, n_swaths), left=0)
    return np.floor(interp_swaths).astype('int')
