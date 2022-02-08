from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from pyuvs.constants import angular_slit_width, minimum_mirror_angle, maximum_mirror_angle
from pyuvs.spectra import fit_templates_to_nightside_data
from pyuvs.swath import swath_number, set_off_disk_pixels_to_nan
from pyuvs.data_files.path import find_latest_apoapse_muv_file_paths_from_block
from pyuvs.data_files.contents import L1bFileCollection, L1bFile
from pyuvs.graphics.colorize import histogram_equalize_detector_image
from pyuvs.graphics.detector_image import make_swath_grid, pcolormesh_detector_image, pcolormesh_rgb_detector_image
from pyuvs.graphics.templates import ApoapseMUVQuicklook, SegmentDetectorImage


def make_dayside_segment_detector_image(orbit: int, data_location: Path, saveloc: str, figheight=6):
    """Make an image of a dayside detector image.

    Parameters
    ----------
    orbit
    data_location
    saveloc
    figheight

    Returns
    -------

    """
    # Load in the data
    data_paths = find_latest_apoapse_muv_file_paths_from_block(data_location, orbit)
    files = [L1bFile(f) for f in data_paths]
    fc = L1bFileCollection(files)

    # Make data that's independent of day/night
    fov = fc.stack_field_of_view()
    swath_numbers = swath_number(fov)
    fc.make_daynight_integration_mask()
    dayside_integration_mask = fc.make_daynight_integration_mask()

    template = SegmentDetectorImage(swath_numbers[-1] + 1, figheight)

    # Do the day/night stuff
    fc.dayside = True
    for daynight in [True]:
        if daynight not in dayside_integration_mask:
            continue
        primary = fc.stack_daynight_calibrated_detector_image()
        on_disk_mask = fc.make_daynight_on_disk_mask()
        daynight_fov = fov[dayside_integration_mask == daynight]
        daynight_swath_number = swath_numbers[dayside_integration_mask == daynight]
        n_spatial_bins = primary.shape[1]

        if daynight:
            # TODO: FF correct here
            rgb_primary = histogram_equalize_detector_image(primary, mask=on_disk_mask) / 255

        for swath in np.unique(swath_numbers):
            # Do this no matter if I'm plotting primary or angles
            swath_inds = daynight_swath_number == swath
            n_integrations = np.sum(swath_inds)
            x, y = make_swath_grid(daynight_fov[swath_inds], swath,
                                   n_spatial_bins, n_integrations)

            # Plot the primary for dayside data
            if daynight:
                pcolormesh_rgb_detector_image(template.data_axis,
                                              rgb_primary[swath_inds], x, y)

    template.data_axis.set_xlim(0, angular_slit_width * (swath_numbers[-1] + 1))
    template.data_axis.set_ylim(minimum_mirror_angle * 2, maximum_mirror_angle * 2)
    template.data_axis.set_xticks([])
    template.data_axis.set_yticks([])
    template.data_axis.set_facecolor('k')
    plt.savefig(saveloc)


def make_apoapse_muv_quicklook(orbit: int, data_location: Path, saveloc: str) -> None:
    """Make the standard apoapse MUV quicklook.

    Parameters
    ----------
    orbit
    data_location
    saveloc

    Returns
    -------
    None

    """
    template = ApoapseMUVQuicklook()
    # Load in the data
    data_paths = find_latest_apoapse_muv_file_paths_from_block(data_location, orbit)
    files = [L1bFile(f) for f in data_paths]
    fc = L1bFileCollection(files)

    # Make data that's independent of day/night
    fov = fc.stack_field_of_view()
    swath_numbers = swath_number(fov)
    fc.make_daynight_integration_mask()
    dayside_integration_mask = fc.make_daynight_integration_mask()

    # Do the day/night stuff
    for daynight in [True, False]:
        fc.dayside = daynight
        if daynight not in dayside_integration_mask:
            continue

        primary = fc.stack_daynight_calibrated_detector_image()
        on_disk_mask = fc.make_daynight_on_disk_mask()
        daynight_fov = fov[dayside_integration_mask == daynight]
        daynight_swath_number = swath_numbers[dayside_integration_mask == daynight]
        sza = set_off_disk_pixels_to_nan(fc.stack_daynight_solar_zenith_angle(), on_disk_mask)
        ea = set_off_disk_pixels_to_nan(fc.stack_daynight_emission_angle(), on_disk_mask)
        pa = set_off_disk_pixels_to_nan(fc.stack_daynight_phase_angle(), on_disk_mask)
        lt = set_off_disk_pixels_to_nan(fc.stack_daynight_local_time(), on_disk_mask)
        n_spatial_bins = primary.shape[1]

        # Do dayside specific things
        if daynight:
            # TODO: FF correct here
            rgb_primary = histogram_equalize_detector_image(primary) / 255
        # Do nightside specific things
        else:
            brightnesses = fit_templates_to_nightside_data(fc)
            no_kR = brightnesses[0, ...]
            aurora_kR = brightnesses[1, ...]

        for swath in np.unique(swath_numbers):
            # Do this no matter if I'm plotting primary or angles
            swath_inds = daynight_swath_number == swath
            n_integrations = np.sum(swath_inds)
            x, y = make_swath_grid(daynight_fov[swath_inds], swath,
                                   n_spatial_bins, n_integrations)
            pcolormesh_detector_image(template.solar_zenith_angle_swath,
                                      sza[swath_inds], x, y,
                                      cmap=template.angle_colormap,
                                      norm=template.angle_norm)
            pcolormesh_detector_image(template.emission_angle_swath,
                                      ea[swath_inds], x, y,
                                      cmap=template.angle_colormap,
                                      norm=template.angle_norm)
            pcolormesh_detector_image(template.phase_angle_swath,
                                      pa[swath_inds], x, y,
                                      cmap=template.angle_colormap,
                                      norm=template.angle_norm)
            pcolormesh_detector_image(template.local_time_swath,
                                      lt[swath_inds], x, y,
                                      cmap=template.local_time_colormap,
                                      norm=template.local_time_norm)

            # Plot the primary for dayside data
            if daynight:
                pcolormesh_rgb_detector_image(template.no_data_swath,
                                              rgb_primary[swath_inds], x, y)
                pcolormesh_rgb_detector_image(template.aurora_data_swath,
                                              rgb_primary[swath_inds], x, y)
            else:
                pcolormesh_detector_image(
                    template.no_data_swath, no_kR[swath_inds], x, y,
                    cmap=template.no_colormap,
                    norm=template.no_norm)
                pcolormesh_detector_image(
                    template.aurora_data_swath, aurora_kR[swath_inds], x, y,
                    cmap=template.aurora_colormap,
                    norm=template.aurora_norm)

    for ax in [template.no_data_swath, template.aurora_data_swath,
               template.solar_zenith_angle_swath,
               template.emission_angle_swath, template.phase_angle_swath,
               template.local_time_swath]:
        ax.set_xlim(0, angular_slit_width * (swath_numbers[-1] + 1))
        ax.set_ylim(minimum_mirror_angle * 2, maximum_mirror_angle * 2)
        ax.set_xticks([])
        ax.set_yticks([])
    plt.savefig(saveloc)


if __name__ == '__main__':
    import time
    o = 5738
    p = Path('/media/kyle/Samsung_T5/IUVS_data')
    sl = f'/home/kyle/ql_testing/segment-quicklook-orbit{o}.pdf'
    make_dayside_segment_detector_image(o, p, sl)
