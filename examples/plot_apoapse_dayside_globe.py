"""
Apoapse Dayside Globe
=====================

Create a standard apoapse MUV globe

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

orbit = 3453
data_path = Path('/media/kyle/Samsung_T5/IUVS_data')
save_location = f'/home/kyle/ql_testing/apoapse-muv-globe-orbit{orbit}.pdf'

# %%
# Load the graphical template where we'll put the images.

# sphinx_gallery_thumbnail_number = -1
fig, ax = plt.subplots()
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


fc.dayside = True

primary = fc.stack_daynight_calibrated_detector_image()
on_disk_mask = fc.make_daynight_on_disk_mask()
daynight_fov = fov[dayside_integration_mask]
daynight_swath_number = swath_numbers[dayside_integration_mask]
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
# TODO: FF correct here
rgb_primary = pu.graphics.histogram_equalize_detector_image(primary) / 255

for swath in np.unique(swath_numbers):
    # Do this no matter if I'm plotting primary or angles
    swath_inds = daynight_swath_number == swath
    n_integrations = np.sum(swath_inds)
    x, y = pu.graphics.make_swath_grid(daynight_fov[swath_inds], swath,
                           n_spatial_bins, n_integrations)

    # Plot the primary for dayside data
    pu.graphics.pcolormesh_rgb_detector_image(template.no_data_swath,
                                  rgb_primary[swath_inds], x, y)
    pu.graphics.pcolormesh_rgb_detector_image(template.aurora_data_swath,
                                  rgb_primary[swath_inds], x, y)

plt.savefig(save_location)
