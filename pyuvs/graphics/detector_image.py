import matplotlib.pyplot as plt
import numpy as np
from pyuvs.constants import angular_slit_width


def pcolormesh_rgb_detector_image(
        axis: plt.Axes, image: np.ndarray, horizontal_meshgrid: np.ndarray,
        vertical_meshgrid: np.ndarray) -> None:
    fill = image[:, :, 0]
    reshaped_image = reshape_data_for_pcolormesh(image)
    plot_detector_image(axis, horizontal_meshgrid, vertical_meshgrid, fill,
                        reshaped_image)


def pcolormesh_detector_image(
        axis: plt.Axes, image: np.ndarray, horizontal_meshgrid: np.ndarray,
        vertical_meshgrid: np.ndarray, cmap, norm) -> None:
    axis.pcolormesh(
        horizontal_meshgrid, vertical_meshgrid, image,
        cmap=cmap,
        norm=norm,
        linewidth=0,
        edgecolors='none',
        rasterized=True)


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


def make_swath_grid(mirror_angles: np.ndarray, swath_number: int,
                    n_positions: int, n_integrations: int) \
        -> tuple[np.ndarray, np.ndarray]:
    """Make a swath grid of mirror angles and spatial bins.

    Parameters
    ----------
    mirror_angles
    swath_number
    n_positions
    n_integrations

    Returns
    -------

    """
    slit_angles = np.linspace(angular_slit_width * swath_number,
                              angular_slit_width * (swath_number + 1),
                              num=n_positions+1)
    mean_angle_difference = np.mean(np.diff(mirror_angles))
    mirror_angles = np.linspace(mirror_angles[0] - mean_angle_difference / 2,
                                mirror_angles[-1] + mean_angle_difference / 2,
                                num=n_integrations + 1) * 2
    return np.meshgrid(slit_angles, mirror_angles)


def make_plot_fill(altitude_mask: np.ndarray) -> np.ndarray:
    """Make the dummy plot fill required for pcolormesh

    Parameters
    ----------
    altitude_mask

    Returns
    -------

    """
    return np.where(altitude_mask, 1, np.nan)


def plot_detector_image(axis: plt.Axes, x: np.ndarray, y: np.ndarray,
                        fill: np.ndarray, colors: np.ndarray) -> None:
    """Plot a detector image created via custom color scheme.

    Parameters
    ----------
    axis
    x
    y
    fill
    colors

    Returns
    -------

    """
    axis.pcolormesh(x, y, fill, color=colors, linewidth=0,
                    edgecolors='none', rasterized=True).set_array(None)
