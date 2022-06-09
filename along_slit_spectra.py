from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from pyuvs.datafiles.contents import L1bFileCollection, L1bFile
from pyuvs.datafiles.path import find_latest_apoapse_muv_file_paths_from_block
from pyuvs import load_flatfield_mid_res_no_app_flip

#files = sorted(Path('/media/kyle/McDataFace/iuvsdata/orbit16300').glob('*apoapse*orbit16308*muv*.gz'))
data_location = Path('/media/kyle/McDataFace/iuvsdata')
orbit = 16308

data_paths = find_latest_apoapse_muv_file_paths_from_block(data_location, orbit)
files = [L1bFile(f) for f in data_paths]
fc = L1bFileCollection(files)

# Get the center lat/lon, rounding to 2 decimals
lat = np.round(fc.stack_daynight_latitude()[:, :, 4], 1)
lon = np.round(fc.stack_daynight_longitude()[:, :, 4], 1)
flat = lat.flatten()
flon = lon.flatten()

# Make a hacked array that's lat/lon smashed together
hack = np.char.add((((flat+90)*100).astype('int')).astype('str'), ((flon*100).astype('int')).astype('str'))
hack = hack.astype('int')

# Get the unique points
unique_vals, unique_idx, unique_counts = np.unique(hack, return_index=True, return_counts=True)
print(unique_idx.shape)

# Make a mask that's True for points that have multiple values
multiple_vals = (unique_counts-1).astype('bool')
print(np.sum(multiple_vals))

# Get the values (lat/lon smashed together) where there are multiple points
# with the same value
multiple_values = hack[unique_idx[multiple_vals]]
print(multiple_values.shape)

mask = np.isin(hack, multiple_values)
print(mask.shape, np.sum(mask))
