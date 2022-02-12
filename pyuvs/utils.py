import numpy as np


def set_off_disk_pixels_to_nan(
        array: np.ndarray, on_disk_mask: np.ndarray) -> np.ndarray:
    """Make a mask of integrations that match the given daynight settings.

    Parameters
    ----------
    array: np.ndarray
        Any array.
    on_disk_mask
        Maks of on-disk pixels. Must be the same shape as array.

    Returns
    -------
    np.ndarray
        Array, where the off disk pixels are np.nans.

    """
    return np.where(on_disk_mask, array, np.nan)
