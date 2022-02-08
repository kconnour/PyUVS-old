"""This module provides functions to help plot detector images.
"""
import matplotlib.pyplot as plt
import numpy as np
from pyuvs.constants import angular_slit_width


def pcolormesh_rgb_detector_image(
        axis: plt.Axes, image: np.ndarray, horizontal_meshgrid: np.ndarray,
        vertical_meshgrid: np.ndarray) -> None:
    """Pcolormesh an rgb detector image in a given axis.

    Parameters
    ----------
    axis: plt.Axes
        The axis to place the pcolormeshed image into.
    image: np.ndarray
        The MxNx3 array of rgb values.
    horizontal_meshgrid: np.ndarray
        The horizontal grid of pixel coordinates.
    vertical_meshgrid: np.ndarray
        The vertical grid of pixel coordinates.

    Returns
    -------
    None

    """
    fill = image[:, :, 0]
    reshaped_image = reshape_data_for_pcolormesh(image)
    plot_detector_image(axis, horizontal_meshgrid, vertical_meshgrid, fill,
                        reshaped_image)


def pcolormesh_detector_image(
        axis: plt.Axes, image: np.ndarray, horizontal_meshgrid: np.ndarray,
        vertical_meshgrid: np.ndarray, **kwargs) -> None:
    """Pcolormesh a single-channel detector image in a given axis.

    Parameters
    ----------
    axis: plt.Axes
        The axis to place the pcolormeshed image into.
    image: np.ndarray
        The MxNx3 array of rgb values.
    horizontal_meshgrid: np.ndarray
        The horizontal grid of pixel coordinates.
    vertical_meshgrid: np.ndarray
        The vertical grid of pixel coordinates.
    **kwargs
        The matplotlib kwargs.

    Returns
    -------
    None

    """

    axis.pcolormesh(
        horizontal_meshgrid, vertical_meshgrid, image,
        linewidth=0,
        edgecolors='none',
        rasterized=True,
        **kwargs)


def reshape_data_for_pcolormesh(image: np.ndarray):
    """Reshape an image array for use in pcolormesh.

    Parameters
    ----------
    image
        Any MxNx3 array.

    Returns
    -------
    np.ndarray
        Array with reshaped dimensions.

    """
    return np.reshape(image, (image.shape[0] * image.shape[1], image.shape[2]))


def make_swath_grid(field_of_view: np.ndarray, swath_number: int,
                    n_positions: int, n_integrations: int) \
        -> tuple[np.ndarray, np.ndarray]:
    """Make a swath grid of mirror angles and spatial bins.

    Parameters
    ----------
    field_of_view: np.ndarray
        The instrument's field of view.
    swath_number: int
        The swath number.
    n_positions: int
        The number of positions.
    n_integrations: int
        The number of integrations.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        The swath grid.

    """
    slit_angles = np.linspace(angular_slit_width * swath_number,
                              angular_slit_width * (swath_number + 1),
                              num=n_positions+1)
    mean_angle_difference = np.mean(np.diff(field_of_view))
    field_of_view = np.linspace(field_of_view[0] - mean_angle_difference / 2,
                                field_of_view[-1] + mean_angle_difference / 2,
                                num=n_integrations + 1)
    return np.meshgrid(slit_angles, field_of_view)


def make_plot_fill(altitude_mask: np.ndarray) -> np.ndarray:
    """Make the dummy plot fill required for pcolormesh

    Parameters
    ----------
    altitude_mask: np.ndarray
        A mask of altitudes.

    Returns
    -------
    np.ndarray
        A plot fill the same shape as altitude_mask.

    """
    return np.where(altitude_mask, 1, np.nan)


def plot_detector_image(axis: plt.Axes, x: np.ndarray, y: np.ndarray,
                        fill: np.ndarray, colors: np.ndarray) -> None:
    """Plot a detector image created via custom color scheme.

    Parameters
    ----------
    axis: plt.Axes
        The axis to place the detector image into.
    x: np.ndarray
        The so called x grid.
    y: np.ndarray
        The so called y grid.
    fill: np.ndarray
        A dummy detector fill.
    colors: np.ndarray
        An MxNx3 array of rgb colors.

    Returns
    -------
    None

    """
    axis.pcolormesh(x, y, fill, color=colors, linewidth=0,
                    edgecolors='none', rasterized=True).set_array(None)
