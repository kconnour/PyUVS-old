from pathlib import Path
import time

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import readsav

from pyuvs.anc import load_midhires_flatfield
from pyuvs.constants import angular_slit_width, minimum_mirror_angle, \
    maximum_mirror_angle
from pyuvs.swath import swath_number
from pyuvs.data_files import L1bFile, \
    find_latest_apoapse_muv_file_paths_from_block, stack_daynight_primary, \
    stack_daynight_solar_zenith_angle, stack_daynight_emission_angle, \
    stack_daynight_phase_angle, stack_daynight_local_time, \
    make_daynight_on_disk_mask, stack_mirror_angles, \
    make_dayside_integration_mask, set_off_disk_pixels_to_nan
from pyuvs.graphics.colorize import turn_primary_to_3_channels, \
    histogram_equalize_rgb_image
from pyuvs.graphics.detector_image import pcolormesh_detector_image, \
    pcolormesh_rgb_detector_image, make_swath_grid
from pyuvs.graphics.templates import ApoapseMUVQuicklook


def make_pipeline_apoapse_muv_quicklook(orbit: int, data_location: Path, save_filename: str) -> None:
    t0 = time.time()
    template = ApoapseMUVQuicklook()
    t1 = time.time()

    # Load in the data
    data_paths = find_latest_apoapse_muv_file_paths_from_block(data_location, orbit)
    files = [L1bFile(f) for f in data_paths]
    t2 = time.time()

    # Make data that's independent of day/night
    mirror_angles = stack_mirror_angles(files)
    swath_numbers = swath_number(mirror_angles)
    dayside_integration_mask = make_dayside_integration_mask(files)

    # Do the day/night stuff
    for daynight in [True, False]:
        if daynight not in dayside_integration_mask:
            continue

        primary = stack_daynight_primary(files, dayside=daynight)
        on_disk_mask = make_daynight_on_disk_mask(files, dayside=daynight)
        daynight_mirror_angles = mirror_angles[dayside_integration_mask == daynight]
        daynight_swath_number = swath_numbers[dayside_integration_mask == daynight]
        sza = set_off_disk_pixels_to_nan(
            stack_daynight_solar_zenith_angle(files, dayside=daynight),
            on_disk_mask)
        ea = set_off_disk_pixels_to_nan(
            stack_daynight_emission_angle(files, dayside=daynight),
            on_disk_mask)
        pa = set_off_disk_pixels_to_nan(
            stack_daynight_phase_angle(files, dayside=daynight),
            on_disk_mask)
        lt = set_off_disk_pixels_to_nan(
            stack_daynight_local_time(files, dayside=daynight),
            on_disk_mask)
        n_spatial_bins = primary.shape[1]

        # Do dayside specific things
        if daynight:
            # TODO: FF correct here
            coadded_primary = turn_primary_to_3_channels(primary)
            rgb_primary = histogram_equalize_rgb_image(coadded_primary, mask=on_disk_mask) / 255
        # Do nightside specific things
        else:
            pass

        for swath in np.unique(swath_numbers):
            # Do this no matter if I'm plotting primary or angles
            swath_inds = daynight_swath_number == swath
            n_integrations = np.sum(swath_inds)
            x, y = make_swath_grid(daynight_mirror_angles[swath_inds], swath, n_spatial_bins, n_integrations)
            pcolormesh_detector_image(template.solar_zenith_angle_swath, sza[swath_inds], x, y, template.angle_colormap, template.angle_norm)
            pcolormesh_detector_image(template.emission_angle_swath,
                                      ea[swath_inds], x, y,
                                      template.angle_colormap,
                                      template.angle_norm)
            pcolormesh_detector_image(template.phase_angle_swath,
                                      pa[swath_inds], x, y,
                                      template.angle_colormap,
                                      template.angle_norm)
            pcolormesh_detector_image(template.local_time_swath,
                                      lt[swath_inds], x, y,
                                      template.local_time_colormap,
                                      template.local_time_norm)

            # Plot the primary for dayside data
            if daynight:
                pcolormesh_rgb_detector_image(template.no_data_swath, rgb_primary[swath_inds], x, y)
                pcolormesh_rgb_detector_image(template.aurora_data_swath, rgb_primary[swath_inds], x, y)

    for ax in [template.no_data_swath, template.aurora_data_swath,
               template.solar_zenith_angle_swath,
               template.emission_angle_swath, template.phase_angle_swath,
               template.local_time_swath]:
        ax.set_xlim(0, angular_slit_width * (swath_numbers[-1] + 1))
        ax.set_ylim(minimum_mirror_angle * 2, maximum_mirror_angle * 2)
        ax.set_xticks([])
        ax.set_yticks([])

    plt.savefig(f'/home/kyle/ql_testing/{save_filename}-orbit{orbit}.pdf')
    t3 = time.time()
    print(t3-t2, t2-t1, t1-t0)


if __name__ == '__main__':
    '''
    # Flatfields
    flatfields = ['MIDRESAPO_FLATFIELD_19X50_ORBIT03733_3739.sav', 'MIDRESAPO_FLATFIELD_19X50_ORBIT03744_3750.sav']

    # Read in data
    p = Path('/media/kyle/Samsung_T5/IUVS_data')
    a = np.load(
        '/home/kyle/repos/PyUVS/pyuvs/anc/mvn_iuv_flatfield.npy',
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
        sza = stack_solar_zenith_angles(files)

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
        template.data_axis.set_facecolor('k')
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

        #print(t2-t1, t1-t0)'''
    p = Path('/media/kyle/Samsung_T5/IUVS_Data')
    make_pipeline_apoapse_muv_quicklook(5675, p, 'quicklooktest')

    '''files = find_latest_apoapse_muv_file_paths_from_block(p, 5675)
    files = [L1bFile(f) for f in files]
    primary = stack_daynight_primary(files, dayside=True)
    altitude_mask = make_daynight_on_disk_mask(files, dayside=True)
    coadded_primary = turn_primary_to_3_channels(primary)
    rgb_primary = histogram_equalize_rgb_image(coadded_primary,
                                               mask=altitude_mask) / 255
    fig, ax = plt.subplots()
    ax.imshow(rgb_primary)
    plt.savefig('/home/kyle/ql_testing/flipstack.pdf')'''
