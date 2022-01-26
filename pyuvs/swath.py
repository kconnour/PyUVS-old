"""

"""
import numpy as np


def swath_number(mirror_angles: np.ndarray) -> np.ndarray:
    """Get the swath number associated with each integration.

    Parameters
    ----------
    mirror_angles
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


def count_integrations_in_swath(
        swath_numbers: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Count the number of integrations that fall in each swath number given
    a mask that selects integrations of interest.

    Parameters
    ----------
    swath_numbers: np.ndarray
        1D array of the swath numbers of each integration.
    mask: np.ndarray
        1D array of booleans, where :code:`True` values indicate integrations
        of interest. Must be the same shape as :code:`swath_numbers`.

    Returns
    -------
    np.ndarray
        The number of integrations in each swath that meet the mask's criteria.

    Examples
    --------
    Count the number of dayside integrations in a fictionalized set of swath
    numbers.

    >>> from pyuvs.swath import count_integrations_in_swath
    >>> swath_numbers = np.array([0, 0, 0, 1, 1, 1])
    >>> dayside_mask = np.array([True, True, False, True, False, False])
    >>> count_integrations_in_swath(swath_numbers, dayside_mask)
    array([2, 1])

    """
    edges = np.concatenate([[-1], np.unique(swath_numbers)]) + 0.5
    return np.histogram(swath_numbers[mask], bins=edges)[0]


def select_integrations_in_swath(
        array: np.ndarray, swath_number: int, swath_numbers: np.ndarray,
        integrations_per_swath: np.ndarray) -> np.ndarray:
    """Select only the data from some array given a desired swath number.

    Parameters
    ----------
    array: np.ndarray
        Any array. The 0th axis is assumed to be the integration axis.
    swath_number
        The swath number to select data from.
    swath_numbers
        1D array of swath numbers.
    integrations_per_swath
        1D array of the number of integrations corresponding to
        :code:`swath_numbers`.

    Returns
    -------
    np.ndarray
        :code:`array`, but trimmed.

    """
    integrations_in_swath = \
        count_integrations_in_swath(swath_numbers, integrations_per_swath)
    edge_inds = np.concatenate([[0], np.cumsum(integrations_in_swath)])
    return array[edge_inds[swath_number]: edge_inds[swath_number + 1], ...]
