from pathlib import Path
from astropy.io import fits
from pyuvs import *

'''for o in range(10, 34):
    p = Path(f'/media/kyle/Samsung_T5/IUVS_data/orbit0{o}00')
    files = sorted(p.glob('*periapse*orbit*muv*.gz'))

    for f in files:
        hdul = fits.open(f)
        print(f)
        s = hdul['primary'].data.shape
        print(s)
        if s[-1] == 1024:
            break'''

p = '/media/kyle/Samsung_T5/IUVS_data/orbit03300/mvn_iuv_l1b_periapse-orbit03334-muv_20160616T054624_v13_r01.fits.gz'
hdul = fits.open(p)
obs = hdul['observation'].data
w = obs['wavelength'][0,0, :]
print(w)
print(load_muv_wavelength_centers())
