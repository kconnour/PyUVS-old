import psycopg
import numpy as np
import matplotlib.pyplot as plt
import glob

import time
from astropy.io import fits

'''files = sorted(glob.glob(f'/media/kyle/Samsung_T5/IUVS_data/orbit03400/*apoapse*{3430}*muv*.gz'))
file = files[9]
print(file)
hdul = fits.open(file)
lat = hdul['pixelgeometry'].data['pixel_corner_lon']
print(np.any(np.isnan(lat[:, 0, :])))

files = sorted(glob.glob(f'/home/kyle/Downloads/*.fits'))
file = files[0]
print(file)
hdul = fits.open(file)
lat = hdul['pixelgeometry'].data['pixel_corner_lon']
print(np.any(np.isnan(lat[:, 0, :])))
raise SystemExit(9)'''
t0 = time.time()
for foo in range(3400, 3430):
    print(f'~~~~~~{foo}~~~~~~~~')
    files = sorted(glob.glob(
        f'/media/kyle/Samsung_T5/IUVS_data/orbit03400/*apoapse*{foo}*muv*.gz'))
    for f in files:
        hdul = fits.open(f)
        lat = hdul['pixelgeometry'].data['pixel_corner_lon']
        np.where((lat > 10) & (lat < 50))

t1 = time.time()
print(t1 - t0)
