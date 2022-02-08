"""This module provides functions to help colorize images.
"""
import numpy as np


def histogram_equalize_grayscale_image(
        image: np.ndarray, mask: np.ndarray = None) -> np.ndarray:
    """Histogram equalize a grayscale image.

    This applies a histogram equalization algorithm to the input image. The
    image can have any shape, though it doesn't make much sense unless it is
    2D.

    Parameters
    ----------
    image
        The image to histogram equalize.
    mask
        A mask of booleans where :code:`False` values are excluded from the
        histogram equalization scaling. This must be the same shape as
        :code:`image`.

    Returns
    -------
    Histogram equalized values ranging from 0 to 255.

    See Also
    --------
    histogram_equalize_rgb_image: Histogram equalize a 3-color channel image.

    Notes
    -----
    I could not get the scikit-learn algorithm to work so I created this.

    The algorithm works like this:

    1. Sort all data used in the coloring.
    2. Use these sorted values to determine the 256 left bin cutoffs.
    3. Linearly interpolate each value in the grid over 256 RGB values and the
       corresponding data values.
    4. Take the floor of the interpolated values since I'm using left cutoffs.

    """
    sorted_values = np.sort(image[mask], axis=None)
    left_cutoffs = np.array([sorted_values[int(i / 256 * len(sorted_values))]
                             for i in range(256)])
    rgb = np.linspace(0, 255, num=256)
    return np.floor(np.interp(image, left_cutoffs, rgb))


def histogram_equalize_rgb_image(
        image: np.ndarray, mask: np.ndarray = None) -> np.ndarray:
    """Histogram equalize an RGB image.

    This applies a histogram equalization algorithm to the input image. The
    RGB dimension is assumed to be the last dimension and should have a length
    of 3. Indices 0, 1, and 2 correspond to R, G, and B, respectively. The
    input image can be any shape, though it doesn't make much sense unless it
    is 3D.

    Parameters
    ----------
    image
        The image to histogram equalize.
    mask
        A mask of booleans where :code:`False` values are excluded from the
        histogram equalization scaling. This must be the same shape as the
        first N-1 dimensions of :code:`image`.

    Returns
    -------
    Histogram equalized values ranging from 0 to 255.

    See Also
    --------
    histogram_equalize_grayscale_image: Histogram equalize a 1-color channel
                                        image.

    """
    red = histogram_equalize_grayscale_image(image[..., 0], mask=mask)
    green = histogram_equalize_grayscale_image(image[..., 1], mask=mask)
    blue = histogram_equalize_grayscale_image(image[..., 2], mask=mask)
    return np.dstack([red, green, blue])


def make_spectral_cutoff_indices(n_wavelengths: int) -> tuple[int, int]:
    """Make the cutoff indices so that the spectral dimension can be
    downsampled to 3 color channels.

    Parameters
    ----------
    n_wavelengths: int
        The number of wavelengths.

    Returns
    -------
    tuple[int, int]
        The blue-green and the green-red cutoff indices.

    """
    blue_green_cutoff = int(n_wavelengths / 3)
    green_red_cutoff = int(n_wavelengths * 2 / 3)
    return blue_green_cutoff, green_red_cutoff


def turn_detector_image_to_3_channels(image: np.ndarray) -> np.ndarray:
    """Turn a detector image into 3 channels by coadding over the spectral
    dimension.

    Parameters
    ----------
    image: np.ndarray
        Any 3D detector image (n_integrations, n_spatial_bins, n_wavelengths).

    Returns
    -------
    np.ndarray
        A co-added detector image (n_integrations, n_spatial_bins, 3).

    """
    n_wavelengths = image.shape[2]
    blue_green_cutoff, green_red_cutoff = \
        make_spectral_cutoff_indices(n_wavelengths)
    red = np.sum(image[..., green_red_cutoff:], axis=-1)
    green = np.sum(image[..., blue_green_cutoff:green_red_cutoff], axis=-1)
    blue = np.sum(image[..., :blue_green_cutoff], axis=-1)
    return np.dstack([red, green, blue])


def histogram_equalize_detector_image(image: np.ndarray, mask=None) -> np.ndarray:
    """

    Parameters
    ----------
    image

    Returns
    -------

    """
    coadded_image = turn_detector_image_to_3_channels(image)
    return histogram_equalize_rgb_image(coadded_image, mask=mask)
