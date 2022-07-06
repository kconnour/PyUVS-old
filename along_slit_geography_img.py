import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from astropy.io import fits
from pathlib import Path
from pyuvs import load_flatfield_mid_res_app_flip
from scipy.interpolate import interp2d, LinearNDInterpolator
from mpl_toolkits.axes_grid1 import make_axes_locatable


data_location = Path('/media/kyle/McDataFace/iuvsdata/stage/orbit16300/')
files = sorted(data_location.glob('*apoapse*orbit16308*muv*s02*.gz'))

# Load in the reference file
hdul = fits.open(files[2])
primary = hdul['primary'].data[:, :, :-1] / load_flatfield_mid_res_app_flip()
lat = hdul['pixelgeometry'].data['pixel_corner_lat'][:, :, 4]
lon = hdul['pixelgeometry'].data['pixel_corner_lon'][:, :, 4]
alt = hdul['pixelgeometry'].data['pixel_corner_mrh_alt'][:, :, 4]

latmin = -52.3 #-44.5  # -52.3
latmax = -49  #42  #-49
lonmin = 360 - 33.7#18.5   #-33.7
lonmax = 360 - 28#-15  #28

# Get the indices of these pixels
latmask = np.bitwise_and((lat >= latmin), (lat <= latmax))
lonmask = np.bitwise_and((lon >= lonmin), (lon <= lonmax))
altmask = alt == 0
mask = np.bitwise_and(np.bitwise_and(latmask, lonmask), altmask).flatten()

latfoo = lat.flatten()[mask]
lonfoo = lon.flatten()[mask]

for j in range(19):
    for counter, i in enumerate([1, 2, 3, 4]):
        test_hdul = fits.open(files[i])
        pri = test_hdul['primary'].data[:, :, :-1] / load_flatfield_mid_res_app_flip()
        la = test_hdul['pixelgeometry'].data['pixel_corner_lat'][:, :, 4]
        lo = test_hdul['pixelgeometry'].data['pixel_corner_lon'][:, :, 4]
        print(i, j)
        if i == 2:
            print(np.array_equal(pri, primary))
        if i == 1:
            fig, ax = plt.subplots(1, 4, figsize=(6, 2))
            divider = make_axes_locatable(ax[-1])
            cax = divider.append_axes('right', size='5%', pad=0.05)
        print('starting interp')
        #interp = interp2d(la.flatten(), lo.flatten(), pri[:, :, j].flatten())
        interp = LinearNDInterpolator(list(zip(la.flatten(), lo.flatten())), pri[:, :, j].flatten())
        print('starting the regrid')
        ans = interp(lat.flatten(), lon.flatten())[mask]
        print('done with the regrid')
        primaryfoo = primary[:, :, j].flatten()[mask]

        ratio = ans / primaryfoo
        print(ratio)

        im = ax[-1 - counter].scatter(lonfoo, latfoo, c=ratio, cmap='viridis', vmin=0.9, vmax=1.2)

        if i == 1:
            fig.colorbar(im, cax=cax, orientation='vertical')
        if i == 4:   # should be 4 eventually
            plt.savefig(f'/home/kyle/iuvs/slit/map/specbin{j}.png', dpi=200)
