import numpy as np


def set_bad_pixels_to_nan(array: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Set The pixels in an array to NaNs given a mask.

    Parameters
    ----------
    array: np.ndarray
        Any array.
    mask
        Maks of desired pixels. Must be the same shape as array.

    Returns
    -------
    np.ndarray
        Array, where the True values in :code:`mask` are left alone and False
        values in :code:`mask` are set to NaNs.

    Examples
    --------
    Make a test set of data and a mask.

    >>> import numpy as np
    >>> import pyuvs as pu
    >>> test_array = np.ones((3, 3))
    >>> diag_mask = np.eye(3, 3).astype('bool')
    >>> pu.set_bad_pixels_to_nan(test_array, diag_mask)
    array([[ 1., nan, nan],
           [nan,  1., nan],
           [nan, nan,  1.]])

    """
    return np.where(mask, array, np.nan)
