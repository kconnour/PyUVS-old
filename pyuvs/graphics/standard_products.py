from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from pyuvs.constants import angular_slit_width, minimum_mirror_angle, maximum_mirror_angle
from pyuvs.spectra import fit_muv_templates_to_nightside_data
from pyuvs.swath import swath_number
from pyuvs.utils import set_bad_pixels_to_nan
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

