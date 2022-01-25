import matplotlib.pyplot as plt
import numpy as np
from pyuvs.graphics.color_transform import turn_primary_to_3_channels, \
    histogram_equalize_rgb_image
from pyuvs.swath import swath_number


def reshape_data_for_pcolormesh(image: np.ndarray):
    return np.reshape(image, (image.shape[0] * image.shape[1], image.shape[2]))


def make_plot_grid(mirror_angles: np.ndarray, swath_number: int, n_positions: int, n_integrations: int):
    x = np.linspace(angular_slit_width * swath_number, angular_slit_width * (swath_number + 1), num=n_positions+1)
    y = np.linspace(mirror_angles[0], mirror_angles[-1], num=n_integrations + 1)
    x = np.flip(x)
    x, y = np.meshgrid(x, y)
    return x, y


def make_plot_fill(altitude_mask: np.ndarray):
    return np.where(altitude_mask, 1, np.nan)


def plot_custom_primary(axis: plt.Axes, x, y, fill, colors):
    img = axis.pcolormesh(x, y, fill, color=colors, linewidth=0, edgecolors='none')
    img.set_array(None)


if __name__ == '__main__':
    from pyuvs.data_files import L1bFile, \
        find_latest_apoapse_muv_file_paths_from_block, stack_dayside_primaries, \
        stack_nightside_primaries, stack_dayside_altitude_center, make_dayside_altitude_mask, \
        stack_mirror_angles, make_dayside_integration_mask
    from pyuvs.constants import angular_slit_width, minimum_mirror_angle, maximum_mirror_angle
    from pathlib import Path
    import time

    # Read in data
    p = Path('/media/kyle/Samsung_T5/IUVS_data')
    o = 5675
    files = find_latest_apoapse_muv_file_paths_from_block(p, o)
    files = [L1bFile(f) for f in files]
    t0 = time.time()

    # Make data that I need
    dayside_primary = stack_dayside_primaries(files)
    nightside_primary = stack_nightside_primaries(files)
    dayside_altitude_mask = make_dayside_altitude_mask(files)
    mirror_angles = stack_mirror_angles(files)
    swath_numbers = swath_number(mirror_angles)
    dayside_integration_mask = make_dayside_integration_mask(files)
    dayside_mirror_angles = mirror_angles[dayside_integration_mask]

    # Color transform
    coadded_primary = turn_primary_to_3_channels(dayside_primary)
    heq_primary = histogram_equalize_rgb_image(coadded_primary, mask=dayside_altitude_mask) / 255
    t1 = time.time()

    # Try out the graphics
    fig, ax = plt.subplots()
    ax.set_xlim(0, 6 * angular_slit_width)
    ax.set_ylim(minimum_mirror_angle, maximum_mirror_angle)

    for i in np.unique(swath_numbers):
        # Get the colorized array + angles of this swath
        swath_rgb = select_info_from_swath(heq_primary, i, swath_numbers, dayside_integration_mask)
        swath_mirror_angles = select_info_from_swath(dayside_mirror_angles, i, swath_numbers, dayside_integration_mask)
        swath_altitude_mask = select_info_from_swath(dayside_altitude_mask, i, swath_numbers, dayside_integration_mask)
        fill = make_plot_fill(swath_altitude_mask)
        x, y = make_plot_grid(swath_mirror_angles, i, swath_rgb.shape[1], swath_rgb.shape[0])   # mirror angles, swath number, n_pos, n_int
        swath_rgb = reshape_data_for_pcolormesh(swath_rgb)
        plot_custom_primary(ax, x, y, fill, swath_rgb)
        #plot_custom_primary(ax, x, y, fill, foo)
    plt.savefig(f'/home/kyle/ql_testing/testql{o}.png')
    t2 = time.time()

    print(t2-t1, t1-t0)
