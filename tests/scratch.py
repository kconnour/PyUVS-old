import numpy as np
from astropy.io import fits

l1b = '/media/kyle/Samsung_T5/IUVS_data/orbit07200/mvn_iuv_l1b_apoapse-orbit07216-muv_20180614T164726_v13_r01.fits.gz'
l1c = '/media/kyle/Samsung_T5/l1c/orbit07200/mvn_iuv_l1c_apoapse-orbit07216-muv_20180614T164726_v13_r01.npy'

b = fits.open(l1b)
c = np.load(l1c, allow_pickle=True)

print(c[37, 102, :])
print(b['pixelgeometry'].data['pixel_corner_lat'][37, 102, :])
