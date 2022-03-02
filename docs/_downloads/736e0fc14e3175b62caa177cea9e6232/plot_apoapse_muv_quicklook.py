"""
Apoapse MUV quicklook
=====================

Create a standard apoapse MUV quicklook.

There are tons of options when it comes to creating images:

* Will the data come from data files or a database?
* Should the dayside coloring use histogram equalization or a linear scaling?
* What templates should be fit to the nightside data?
* Will there be a dayside mask that sets the coloring?

It's therefore nearly impossible to create a function that handles all the
potential options. This example will walk through how to create a standard
apoapse quicklook. It uses data from data files, uses dayside histogram
equalization, and fits 4 templates to nightside data.

"""

# %%
# Import everything we'll need.

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pyuvs as pu

# %%
# Set variables on where we'll pull the data from and where we'll save the
# data. Note that if you turn this into a function, these will be the only
# required inputs.

orbit = 5738
data_path = Path('/media/kyle/Samsung_T5/IUVS_data')
save_location = f'/home/kyle/ql_testing/apoapse-muv-quicklook-orbit{orbit}.pdf'

# %%
# Load the graphical template where we'll put the images.

# sphinx_gallery_thumbnail_number = -1
template = pu.graphics.ApoapseMUVQuicklook()
# sphinx_gallery_defer_figures

# %%
# Load in the data into a file collection. This object will help us pull the
# info from the IUVS files that we need.

data_paths = pu.datafiles.find_latest_apoapse_muv_file_paths_from_block(
    data_path, orbit)
files = [pu.datafiles.L1bFile(f) for f in data_paths]
fc = pu.datafiles.L1bFileCollection(files)
# sphinx_gallery_defer_figures

# %%
# Make the data that's independent of day/night.

fov = fc.stack_field_of_view()
swath_numbers = pu.swath_number(fov)
fc.make_daynight_integration_mask()
dayside_integration_mask = fc.make_daynight_integration_mask()
# sphinx_gallery_defer_figures

# %%
# Stack pixels that are either dayside or nightside. Plot them

for daynight in [True, False]:
    fc.dayside = daynight
    if daynight not in dayside_integration_mask:
        continue

    primary = fc.stack_daynight_calibrated_detector_image()
    on_disk_mask = fc.make_daynight_on_disk_mask()
    daynight_fov = fov[dayside_integration_mask == daynight]
    daynight_swath_number = swath_numbers[dayside_integration_mask == daynight]
    sza = pu.set_bad_pixels_to_nan(
        fc.stack_daynight_solar_zenith_angle(), on_disk_mask)
    ea = pu.set_bad_pixels_to_nan(
        fc.stack_daynight_emission_angle(), on_disk_mask)
    pa = pu.set_bad_pixels_to_nan(
        fc.stack_daynight_phase_angle(), on_disk_mask)
    lt = pu.set_bad_pixels_to_nan(
        fc.stack_daynight_local_time(), on_disk_mask)
    n_spatial_bins = primary.shape[1]

    # Do dayside specific things
    if daynight:
        # TODO: FF correct here
        rgb_primary = pu.graphics.histogram_equalize_detector_image(primary) / 255
    # Do nightside specific things
    else:
        dds = fc.stack_detector_image_dark_subtracted()
        dn_unc = fc.stack_detector_image_random_uncertainty_dn()
        file = fc.get_first_nightside_file()

        spbw = int(np.median(file.binning.spectral_pixel_bin_width))
        ssi = int(file.binning.spectral_pixel_bin_width[0] / spbw)
        spapbw = int(np.median(file.binning.spatial_pixel_bin_width))
        ww = np.median(file.observation.wavelength_width)
        vg = file.observation.voltage_gain
        it = file.observation.integration_time

        brightnesses = pu.fit_muv_templates_to_nightside_data(
            dds, dn_unc, ww, spapbw, spbw, ssi, vg, it)
        no_kR = brightnesses[0, ...]
        aurora_kR = brightnesses[1, ...]

    for swath in np.unique(swath_numbers):
        # Do this no matter if I'm plotting primary or angles
        swath_inds = daynight_swath_number == swath
        n_integrations = np.sum(swath_inds)
        x, y = pu.graphics.make_swath_grid(daynight_fov[swath_inds], swath,
                               n_spatial_bins, n_integrations)
        pu.graphics.pcolormesh_detector_image(
            template.solar_zenith_angle_swath,
            sza[swath_inds], x, y,
            cmap=template.angle_colormap,
            norm=template.angle_norm)
        pu.graphics.pcolormesh_detector_image(template.emission_angle_swath,
                                  ea[swath_inds], x, y,
                                  cmap=template.angle_colormap,
                                  norm=template.angle_norm)
        pu.graphics.pcolormesh_detector_image(template.phase_angle_swath,
                                  pa[swath_inds], x, y,
                                  cmap=template.angle_colormap,
                                  norm=template.angle_norm)
        pu.graphics.pcolormesh_detector_image(template.local_time_swath,
                                  lt[swath_inds], x, y,
                                  cmap=template.local_time_colormap,
                                  norm=template.local_time_norm)

        # Plot the primary for dayside data
        if daynight:
            pu.graphics.pcolormesh_rgb_detector_image(template.no_data_swath,
                                          rgb_primary[swath_inds], x, y)
            pu.graphics.pcolormesh_rgb_detector_image(template.aurora_data_swath,
                                          rgb_primary[swath_inds], x, y)
        else:
            pu.graphics.pcolormesh_detector_image(
                template.no_data_swath, no_kR[swath_inds], x, y,
                cmap=template.no_colormap,
                norm=template.no_norm)
            pu.graphics.pcolormesh_detector_image(
                template.aurora_data_swath, aurora_kR[swath_inds], x, y,
                cmap=template.aurora_colormap,
                norm=template.aurora_norm)
# sphinx_gallery_defer_figures

# %%
# Set the axis limits in the subplots

for ax in [template.no_data_swath, template.aurora_data_swath,
           template.solar_zenith_angle_swath,
           template.emission_angle_swath, template.phase_angle_swath,
           template.local_time_swath]:
    ax.set_xlim(0, pu.angular_slit_width * (swath_numbers[-1] + 1))
    ax.set_ylim(pu.minimum_mirror_angle * 2, pu.maximum_mirror_angle * 2)
    ax.set_xticks([])
    ax.set_yticks([])
plt.savefig(save_location)
