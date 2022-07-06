from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from pyuvs.datafiles.contents import L1bFileCollection, L1bFile
from pyuvs.datafiles.path import find_latest_apoapse_muv_file_paths_from_block
from pyuvs import load_flatfield_mid_res_no_app_flip

#files = sorted(Path('/media/kyle/McDataFace/iuvsdata/orbit16300').glob('*apoapse*orbit16308*muv*.gz'))
data_location = Path('/media/kyle/McDataFace/iuvsdata/stage')
orbit = 16308

data_paths = find_latest_apoapse_muv_file_paths_from_block(data_location, orbit)
files = [L1bFile(f) for f in data_paths]
fc = L1bFileCollection(files)

# Get the center lat/lon, rounding to N decimals
alt = fc.stack_daynight_altitude_center()
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
multiple_vals = np.where(unique_counts > 2, True, False)
print(np.sum(multiple_vals))

# Get the values (lat/lon smashed together) where there are multiple points
# with the same value
multiple_values = hack[unique_idx[multiple_vals]]
print(multiple_values.shape)

# Make a mask of values that have duplicates and make it the data shape.
# We're now done with this part
mask = np.isin(hack, multiple_values)
mask = mask.reshape(lat.shape)

mask = np.bitwise_and(mask, alt == 0)

# FF correct the data
primary = fc.stack_daynight_calibrated_detector_image()
primary = primary[:, :, :-1] / load_flatfield_mid_res_no_app_flip()

slitpos = np.broadcast_to(np.arange(0, 50), lat.shape)
idk = slitpos[mask]

answer = np.zeros((50, 19))
slit = np.linspace(0.5, 49.5, num=50)

for spec_idx in range(19):
    p = primary[:, :, spec_idx][mask]
    print('~'*30)
    print(p.shape)

    # Throw away percentiles
    percentile_inds = (p < np.percentile(p, 66)) & (p > np.percentile(p, 33))
    p = p[percentile_inds]
    percentile_slit = idk[percentile_inds]

    print(p.shape)

    fig, ax = plt.subplots()
    ax.scatter(percentile_slit, p)

    fit = np.polyfit(percentile_slit, p, 2)
    poly = np.poly1d(fit)
    solution = poly(percentile_slit)
    ax.scatter(percentile_slit, solution, color='r')

    fuckthis = poly(slit)

    crapvar = fuckthis[10]
    crappiervar = 1 / (fuckthis / crapvar)
    answer[:, spec_idx] = crappiervar



    #ax.set_ylim(0, 5000)

    #plt.savefig(f'/home/kyle/iuvs/slit/specbin{spec_idx}')
    plt.close(fig)


np.save('/home/kyle/iuvs/slit/slit_correction_3points.npy', answer)
