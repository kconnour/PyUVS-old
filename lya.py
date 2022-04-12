from pathlib import Path
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from lmfit.models import PseudoVoigtModel
#from scipy.io import readsav

#justin = readsav('/home/kyle/Downloads/mvn_iuv_apoapse_lya_centroid_37xx.sav')
#centroid = justin['centroid'].T   # shape = (position, integration, file) = (10, 255, 1164)
#jfiles = justin['file_array']

p = Path('/media/kyle/Samsung_T5/IUVS_data/orbit03400')
fuv_files = sorted(p.glob('*apoapse*fuv*.gz'))
muv_files = sorted(p.glob('*apoapse*muv*.gz'))

fuv_files = [fuv_files[0]]

hdulmuv = fits.open(muv_files[0])
muvwavs = hdulmuv['observation'].data['wavelength'][-1, -1, :]
spapixlo = hdulmuv['binning'].data['spapixlo'][-1, :]
spepixlo = hdulmuv['binning'].data['spepixlo'][-1, :]
spepixhi = hdulmuv['binning'].data['spepixhi'][-1, :]


#fig, ax = plt.subplots()
#ax.set_xlim(5.25e8, 5.27e8)
#ax.set_ylim(171, 178)

kcent = np.zeros((10,))
for f in fuv_files:
    hdul = fits.open(f)
    #hdul.info()  # (206, 10, 153)
    primary = hdul['primary'].data
    fuv_binning = hdul['binning'].data
    fuv_spapixlo = fuv_binning['spapixlo'][-1, :]  # (n_positions)
    fuv_spepixlo = fuv_binning['spepixlo'][-1, :] + 2  # (n_wavelengths)
    fuv_wavelength = hdul['observation'].data['wavelength'][-1, -1, :]

    #for integration in range(primary.shape[0]):
    for integration in [-1]:
        print(integration)
        for position in range(primary.shape[1]):
            mod = PseudoVoigtModel()
            try:
                pars = mod.guess(primary[integration, position, :], x=fuv_spepixlo)
            except IndexError:
                continue
            out = mod.fit(primary[integration, position, :], pars, x=fuv_spepixlo)
            #report = out.fit_report(min_correl=0.25)
            center = out.params['center'].value
            kcent[position] = center
            #ax.scatter(et[integration], center, s=1)

fuv_spa_bindiff = np.median(np.abs(np.diff(fuv_spapixlo)))
fuv_spa_bincenter = fuv_spa_bindiff // 2 + fuv_spapixlo
muv_spa_bindiff = np.median(np.abs(np.diff(spapixlo)))
muv_spa_bincenter = muv_spa_bindiff // 2 + spapixlo

lya_true_position = np.interp(121.565, fuv_wavelength, fuv_spepixlo)
fuv_pixel_diff = lya_true_position - kcent
muv_pixel_diff = 0.92 * fuv_pixel_diff

binoffset = np.interp(muv_spa_bincenter, fuv_spa_bincenter, muv_pixel_diff)
print(binoffset)
np.save('/home/kyle/ql_testing/binoffset.npy', binoffset)

'''fig, ax = plt.subplots(1, 10)
hdul = fits.open(fuv_files[0])
prim = hdul['primary'].data
for i in range(10):
    ax[i].plot(fuv_wavelength, prim[-1, i, :])


plt.savefig('/home/kyle/ql_testing/fuv_spectra.png')'''
