from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
import glob
from scipy.io import readsav


from pyuvs.datafiles.path import find_latest_apoapse_muv_file_paths_from_block

data_location = Path('/media/kyle/McDataFace/iuvsdata/stage')

latmin = -52.3#-48 # -52.3 #-29.5 #-52.3
latmax = -49#-46 # -49 # -27.5 #-49
lonmin = 360 - 33.7#360 - 71.1 #360 - 33.7 # 360 - 52 #360 - 33.7
lonmax = 360 - 28#360 - 68.6 # 360 - 28 # 360 - 49.8 #360 - 28

orbit = 16308
data_paths = find_latest_apoapse_muv_file_paths_from_block(data_location, orbit)
l1c = sorted(glob.glob('/home/kyle/iuvs/reflectance/orbit16300/*-linear.npy'))
files = sorted(glob.glob('/home/kyle/iuvs/wavelengths/broken-spacecraft/*orbit16308*.sav'))

fig, ax = plt.subplots()

for counter, file in enumerate(data_paths):
    hdul = fits.open(file)
    lat = hdul['pixelgeometry'].data['pixel_corner_lat'][:, :, 4]
    lon = hdul['pixelgeometry'].data['pixel_corner_lon'][:, :, 4]
    alt = hdul['pixelgeometry'].data['pixel_corner_mrh_alt'][:, :, 4]

    primary = np.load(l1c[counter])

    wavelengths_grid = readsav(files[counter])['wavelength_muv']

    # Get the indices of these pixels
    latmask = np.bitwise_and((lat >= latmin), (lat <= latmax))
    lonmask = np.bitwise_and((lon >= lonmin), (lon <= lonmax))
    altmask = alt == 0
    mask = np.bitwise_and(np.bitwise_and(latmask, lonmask), altmask)
    slit = np.broadcast_to(np.arange(0, 50), lat.shape)
    slitpos = slit[mask]

    primary = primary[mask, :]

    print(primary.shape, slitpos.shape)

    for c, i in enumerate(slitpos):
        w = wavelengths_grid[i, :-1]
        if counter == 1:
            col = 'r'
        elif counter == 2:
            col = 'g'
            w = w + 0.75
        elif counter == 3:
            col = 'b'
            w = w + 1.5
        elif counter == 4:
            col = 'k'
            w = w + 2.25
        ax.scatter(w, primary[c, :], color=col)

ax.set_xlabel('Wavelength (nm)')
ax.set_ylabel('Reflectance')
plt.savefig('/home/kyle/iuvs/slit/if-linear.png', dpi=200)
