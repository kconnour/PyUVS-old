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


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about the given axis by theta radians.
    To transform a vector, calculate its dot-product with the rotation matrix.

    Parameters
    ----------
    axis : 3-element list, array, or tuple
        The rotation axis in Cartesian coordinates. Does not have to be a unit vector.
    theta : float
        The angle (in radians) to rotate about the rotation axis. Positive angles rotate counter-clockwise.

    Returns
    -------
    matrix : array
        The 3D rotation matrix with dimensions (3,3).
    """

    # convert the axis to a numpy array and normalize it
    axis = np.array(axis)
    axis = axis / np.linalg.norm(axis)

    # calculate components of the rotation matrix elements
    a = np.cos(theta / 2)
    b, c, d = -axis * np.sin(theta / 2)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d

    # build the rotation matrix
    matrix = np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                       [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                       [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

    # return the rotation matrix
    return matrix
