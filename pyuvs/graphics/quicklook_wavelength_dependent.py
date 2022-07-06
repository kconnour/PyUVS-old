from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from pyuvs.constants import angular_slit_width, minimum_mirror_angle, maximum_mirror_angle
from pyuvs.spectra import fit_muv_templates_to_nightside_data
from pyuvs.swath import swath_number
from pyuvs.datafiles.path import find_latest_apoapse_muv_file_paths_from_block
from pyuvs.datafiles.contents import L1bFileCollection, L1bFile
from pyuvs.graphics.colorize import histogram_equalize_detector_image
from pyuvs.graphics.detector_image import make_swath_grid, pcolormesh_detector_image, pcolormesh_rgb_detector_image
from pyuvs.graphics.templates import ApoapseMUVQuicklook, SegmentDetectorImage
from pyuvs import load_flatfield_mid_res_no_app_flip, load_flatfield_mid_res_app_flip, load_flatfield_mid_hi_res_update, load_flatfield_mid_hi_res_my34gds
from astropy.io import fits
import glob
from scipy.io import readsav
from scipy.interpolate import LinearNDInterpolator, interp2d


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
    data_paths = sorted(find_latest_apoapse_muv_file_paths_from_block(data_location, orbit))
    hduls = [fits.open(f) for f in data_paths]

    # Make data that's independent of day/night
    fov = np.concatenate([hdul['integration'].data['fov_deg'] for hdul in hduls])
    swath_numbers = swath_number(fov)
    # Hack: make daynight mask
    dayside_integration_mask = np.repeat(True, swath_numbers.shape)

    # Make the template
    template = SegmentDetectorImage(swath_numbers[-1] + 1, figheight)

    # Get wavelengths, both the OG ones and Justin's
    wavelength_files = sorted(glob.glob(f'/home/kyle/iuvs/wavelengths/broken-spacecraft-nonlin/*orbit{orbit}*.sav'))
    og_wavs = hduls[0]['observation'].data['wavelength'][0][0, :-1]

    # Semi-hackishly make the flatfield-corrected, wavelength-dependent primary array
    primaries = []
    l1c = sorted(glob.glob(f'/home/kyle/iuvs/reflectance/orbit16400/*'))

    for counter, hdul in enumerate(hduls):
        primary = hdul['primary'].data

        # Get the corresponding wavelengths
        wavelengths_grid = readsav(wavelength_files[counter])['wavelength_muv']  # (133/50, 19/20) --- the same shape as the .fits structure

        # Hack: instead of integration, just interpolate the flatfield to the new wavelength grid
        spatial_bins = np.arange(primary.shape[1])
        ff = load_flatfield_mid_res_app_flip()

        new_ff = np.zeros((primary.shape[1:]))
        for spabin in spatial_bins:
            new_ff[spabin, :] = np.interp(wavelengths_grid[spabin, :], og_wavs, ff[spabin, :])

        primary = primary / new_ff
        primaries.append(primary)
        #primaries.append(np.load(l1c[counter]))

    primary = np.vstack(primaries)
    print(primary.shape)

    # APP flip the stuff here
    primary = np.fliplr(primary)

    for daynight in [True]:
        on_disk_mask = np.vstack([hdul['pixelgeometry'].data['pixel_corner_mrh_alt'][..., 4] for hdul in hduls]) == 0
        daynight_mask = dayside_integration_mask == daynight
        daynight_fov = fov[daynight_mask]
        daynight_swath_number = swath_numbers[daynight_mask]
        n_spatial_bins = primary.shape[1]

        if daynight:
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


if __name__ == '__main__':
    p = Path('/media/kyle/McDataFace/iuvsdata/stage')
    for o in [16407]:
        make_dayside_segment_detector_image(o, p, f'/home/kyle/iuvs/ql/orbit16400/orbit{o}-wavdependent-nonlin.png')

