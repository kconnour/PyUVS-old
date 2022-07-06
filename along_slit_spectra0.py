from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits

from pyuvs.datafiles.contents import L1bFileCollection, L1bFile
from pyuvs.datafiles.path import find_latest_apoapse_muv_file_paths_from_block
from pyuvs import load_flatfield_mid_res_no_app_flip, load_flatfield_mid_res_app_flip

data_location = Path('/media/kyle/McDataFace/iuvsdata/stage')

latmin = -52.3#-48 # -52.3 #-29.5 #-52.3
latmax = -49#-46 # -49 # -27.5 #-49
lonmin = 360 - 33.7#360 - 71.1 #360 - 33.7 # 360 - 52 #360 - 33.7
lonmax = 360 - 28#360 - 68.6 # 360 - 28 # 360 - 49.8 #360 - 28

orbit = 16410
data_paths = find_latest_apoapse_muv_file_paths_from_block(data_location, orbit)
#files = [L1bFile(f) for f in data_paths]
#fc = L1bFileCollection(files)
hduls = [fits.open(f) for f in data_paths]
lat = np.vstack([f['pixelgeometry'].data['pixel_corner_lat'][:, :, 4] for f in hduls])
lon = np.vstack([f['pixelgeometry'].data['pixel_corner_lon'][:, :, 4] for f in hduls])
alt = np.vstack([f['pixelgeometry'].data['pixel_corner_mrh_alt'][:, :, 4] for f in hduls])

#print(files[0].is_app_flipped())
#raise SystemExit(9)

#lat = fc.stack_daynight_latitude()[:, :, 4]
#lon = fc.stack_daynight_longitude()[:, :, 4]
#alt = fc.stack_daynight_altitude_center()
slit = np.broadcast_to(np.arange(0, 50), lat.shape)

# Note: fliplr = flip(axis=1), which for the primary is the spatial bin
# dimension. flipud = flip(axis=0), which for the flatfield is the spatial
# bin dimesion. primary = (n_integrations, n_spatial, n_spectral).
# ff = (n_spatial, n_spectral)

#primary = fc.stack_daynight_calibrated_detector_image()
#primary = primary[:, :, :-1] / np.flipud(load_flatfield_mid_res_app_flip())
primary = np.vstack([f['primary'].data[:, :, :-1] for f in hduls])
primary = primary / load_flatfield_mid_res_app_flip()

# Get the indices of these pixels
latmask = np.bitwise_and((lat >= latmin), (lat <= latmax))
lonmask = np.bitwise_and((lon >= lonmin), (lon <= lonmax))
altmask = alt == 0
mask = np.bitwise_and(np.bitwise_and(latmask, lonmask), altmask)
slitpos = slit[mask]

foo = np.zeros((50, 19))
fakeslit = np.linspace(0.5, 49.5, num=50)

for i in range(19):
    p = primary[:, :, i][mask]

    fig, ax = plt.subplots()
    ax.scatter(slitpos, p)

    fit = np.polyfit(slitpos, p, 5)
    poly = np.poly1d(fit)
    solution = poly(fakeslit)
    ax.scatter(fakeslit, solution, color='r')

    plt.savefig(f'/home/kyle/iuvs/slit/hf-crater-16410/orbit16410-specbin{i}.png')
    foo[:, i] = 1 / (solution / solution[6])

np.save(f'/home/kyle/iuvs/slit/hf-crater-16410/orbit16410-correction.npy', foo)
