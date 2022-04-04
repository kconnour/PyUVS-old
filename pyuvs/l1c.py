import warnings
from pathlib import Path

import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from data_converter import *
from pyuvs.datafiles import L1bFile
from pyuvs.spectra import calculate_calibration_curve, rebin_muv_wavelengths
from pyuvs import *
from scipy.integrate import quadrature


wav_edges = load_muv_wavelength_edges()
sspath = '/home/kyle/solar/solar_flux_solstice_muv_201606.txt'
ss = np.genfromtxt(sspath)  # 0 is wav, 1 is spectrum, 2 is unc

l1cp = '/media/kyle/Samsung_T5/l1ctxt/orbit03400/mvn_iuv_l1c_apoapse-orbit03400-muv_20160628T104609_v13_r01.txt'
l1c = L1CTxt(l1cp)

p = Path('/media/kyle/Samsung_T5/IUVS_data/orbit03400')
files = sorted(p.glob('*apoapse*3400*muv*.gz'))

hdul = fits.open(files[0])

binwid = hdul['binning'].data['spebinwidth'][0]
lo = hdul['binning'].data['spepixlo'][0]
hi = hdul['binning'].data['spepixlo'][0]

#solar = load_template_solar_continuum()

file = L1bFile(files[0])

wavs = file.observation.wavelength[0, :]
wavdiff = np.median(np.abs(np.diff(wavs)))
wavedge = np.concatenate((np.array([wavs[0] - wavdiff/2]), wavs + wavdiff/2))

detector_wavs = np.concatenate((file.binning.spectral_pixel_low[0, :], np.array([818])))
wavedge = wav_edges[detector_wavs]


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


def solar(wav):
    return np.interp(wav, ss[:, 0], ss[:, 1])


def integrate_solar(low, high):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return quadrature(solar, low, high)[0]


intsolar = np.array([integrate_solar(wavedge[i], wavedge[i+1]) for i in range(len(wavs))])
foobar = intsolar
kyleflux = foobar * ww

baz = file.detector_image.calibrated[-1, -1, :] * wavdiff * 10e-9
franckflux = baz * np.pi / (np.cos(np.radians(file.pixel_geometry.solar_zenith_angle[-1, -1]))) / l1c.reflectance[-1, -1, :]

test = file.detector_image.calibrated[-1, -1, :] * ww * np.pi / np.cos(np.radians(file.pixel_geometry.solar_zenith_angle[-1, 1]))
print(test / intsolar * 10e-9)

#plt.plot(wavs, kyleflux / franckflux)
#plt.savefig('/home/kyle/ql_testing/flux.png')
'''
for i in range(19):
    offset = 0
    foo[i] = np.sum(solar[lo[i] + offset: hi[i]+1 + offset])
    binsolar[i] = np.sum(solar[lo[i]: hi[i]+1])

reference = foo/binsolar * ww / rebinned_calibration_curve
foobar = reference * 6241 / 0.00691361
print(l1c.solar_flux[-1, -1, :] / foobar)
raise SystemExit(9)


for counter, j in enumerate([-3, -2, -1, 0, 1, 2, 3]):
    offset = j
    for i in range(19):
        ref = wavs, foo/binsolar * ww / rebinned_calibration_curve

        foo[i] = np.sum(solar[lo[i] + offset: hi[i]+1 + offset])
        binsolar[i] = np.sum(solar[lo[i]: hi[i]+1])'''

