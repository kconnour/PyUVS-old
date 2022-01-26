import matplotlib.pyplot as plt
import numpy as np
from pyuvs.graphics.colorize import turn_primary_to_3_channels, \
    histogram_equalize_rgb_image
from pyuvs.swath import swath_number


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
    mirror_angles = np.linspace(mirror_angles[0], mirror_angles[-1],
                                num=n_integrations + 1)
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
                    edgecolors='none').set_array(None)


if __name__ == '__main__':
    from pyuvs.data_files import L1bFile, \
        find_latest_apoapse_muv_file_paths_from_block, stack_dayside_primaries, \
        stack_nightside_primaries, make_dayside_altitude_mask, \
        stack_mirror_angles, make_dayside_integration_mask
    from pyuvs.constants import angular_slit_width, minimum_mirror_angle, maximum_mirror_angle
    from pathlib import Path
    import time
    from pyuvs.swath import select_integrations_in_swath
    from scipy.io import readsav
    from pyuvs.graphics.templates import SegmentDetectorImage

    # Flatfields
    flatfields = ['MIDRESAPO_FLATFIELD_19X50_ORBIT03733_3739.sav', 'MIDRESAPO_FLATFIELD_19X50_ORBIT03744_3750.sav']

    # Read in data
    p = Path('/media/kyle/Samsung_T5/IUVS_data')
    a = np.load(
        '/home/kyle/repos/PyUVS/pyuvs-old/anc/files/mvn_iuv_flatfield.npy',
        allow_pickle=True).item()['flatfield']
    orbits = [3734, 3741, 3744, 3748]
    #orbits = [3734]
    t0 = time.time()
    for o in orbits:
        print(o)
        files = find_latest_apoapse_muv_file_paths_from_block(p, o)
        files = [L1bFile(f) for f in files]

        # REscale FF
        newff = np.zeros((50, 19))
        for i in range(19):
            foo = np.linspace(0, 132, num=50)
            bar = np.linspace(0, 132, num=133)
            newff[:, i] = np.interp(foo, bar, a[:, i])

        #t0 = time.time()

        if o in [3744, 3748]:
            flip = True
            ff = readsav(f'/home/kyle/ql_testing/{flatfields[1]}')
            ff = ff['midresapo_flatfield_19x50_orbit03744_3750']
        else:
            flip = False
            ff = readsav(f'/home/kyle/ql_testing/{flatfields[0]}')
            ff = ff['midresapo_flatfield_19x50_orbit03733_3739']
        ff = newff
        # Make data that I need
        dayside_primary = stack_dayside_primaries(files)
        #nightside_primary = stack_nightside_primaries(files)
        dayside_altitude_mask = make_dayside_altitude_mask(files)
        mirror_angles = stack_mirror_angles(files)
        swath_numbers = swath_number(mirror_angles)
        dayside_integration_mask = make_dayside_integration_mask(files)
        dayside_mirror_angles = mirror_angles[dayside_integration_mask]

        # Flatfield correct
        ff = np.broadcast_to(ff, dayside_primary.shape)
        dayside_primary = dayside_primary / ff

        if flip:
            dayside_primary = np.fliplr(dayside_primary)
            dayside_altitude_mask = np.fliplr(dayside_altitude_mask)

        # Color transform
        coadded_primary = turn_primary_to_3_channels(dayside_primary)
        heq_primary = histogram_equalize_rgb_image(coadded_primary, mask=dayside_altitude_mask) / 255
        #t1 = time.time()

        # Try out the graphics
        template = SegmentDetectorImage(6, 5)
        template.data_axis.set_xlim(0, 6*angular_slit_width)
        template.data_axis.set_ylim(minimum_mirror_angle, maximum_mirror_angle)
        #template.data_axis.set_facecolor('k')
        template.data_axis.set_xticks([])
        template.data_axis.set_yticks([])
        #fig, ax = plt.subplots()
        #ax.set_xlim(0, 6 * angular_slit_width)
        #ax.set_ylim(minimum_mirror_angle, maximum_mirror_angle)

        for i in np.unique(swath_numbers):
            # Get the colorized array + angles of this swath
            swath_rgb = select_integrations_in_swath(heq_primary, i, swath_numbers, dayside_integration_mask)
            swath_mirror_angles = select_integrations_in_swath(dayside_mirror_angles, i, swath_numbers, dayside_integration_mask)
            swath_altitude_mask = select_integrations_in_swath(dayside_altitude_mask, i, swath_numbers, dayside_integration_mask)
            fill = make_plot_fill(swath_altitude_mask)
            x, y = make_swath_grid(swath_mirror_angles, i, swath_rgb.shape[1], swath_rgb.shape[0])   # mirror angles, swath number, n_pos, n_int
            swath_rgb = reshape_data_for_pcolormesh(swath_rgb)
            plot_detector_image(template.data_axis, x, y, fill, swath_rgb)
            #plot_custom_primary(ax, x, y, fill, foo)
        plt.savefig(f'/home/kyle/ql_testing/testql{o}_oldFF.png')
        #t2 = time.time()
        t1 = time.time()
        print(t1-t0)

        #print(t2-t1, t1-t0)

