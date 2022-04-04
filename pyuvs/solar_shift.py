from pyuvs import *
from astropy.io import fits
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from pyuvs.datafiles import L1bFile
from pyuvs.spectra import calculate_calibration_curve, rebin_muv_wavelengths

p = Path('/media/kyle/Samsung_T5/IUVS_data/orbit03400')
files = sorted(p.glob('*apoapse*3453*muv*.gz'))

hdul = fits.open(files[0])

binwid = hdul['binning'].data['spebinwidth'][0]
lo = hdul['binning'].data['spepixlo'][0]
hi = hdul['binning'].data['spepixlo'][0]

solar = load_template_solar_continuum()

file = L1bFile(files[0])
wavs = np.linspace(205, 306, num=19)

spbw = int(np.median(file.binning.spectral_pixel_bin_width))
ssi = int(file.binning.spectral_pixel_bin_width[0] / spbw)
spapbw = int(np.median(file.binning.spatial_pixel_bin_width))
ww = np.median(file.observation.wavelength_width)
vg = file.observation.voltage_gain
it = file.observation.integration_time

rebinned_sensitivity_curve = np.interp(
    wavs,
    load_muv_sensitivity_curve_observational()[:, 0],
    load_muv_sensitivity_curve_observational()[:, 1])

rebinned_calibration_curve = calculate_calibration_curve(
    rebinned_sensitivity_curve,
    spapbw, ww,
    vg, it)

fig, ax = plt.subplots(1, 7, figsize=(14, 2))
binsolar = np.zeros((19,))
foo = np.zeros((19,))

for i in range(19):
    offset = 0
    foo[i] = np.sum(solar[lo[i] + offset: hi[i]+1 + offset])
    binsolar[i] = np.sum(solar[lo[i]: hi[i]+1])

reference = foo/binsolar * ww / rebinned_calibration_curve


for counter, j in enumerate([-3, -2, -1, 0, 1, 2, 3]):
    offset = j
    for i in range(19):
        ref = wavs, foo/binsolar * ww / rebinned_calibration_curve

        foo[i] = np.sum(solar[lo[i] + offset: hi[i]+1 + offset])
        binsolar[i] = np.sum(solar[lo[i]: hi[i]+1])

    ax[counter].plot(wavs, 1 / ((foo/binsolar * ww / rebinned_calibration_curve) / reference))
    ax[counter].set_xticks([220, 260, 300])

    #ax[counter].set_ylim(0, 0.01)

plt.savefig('/home/kyle/solargrid.png')
