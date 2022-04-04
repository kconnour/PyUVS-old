import warnings
from pathlib import Path

import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from pyuvs.datafiles import L1bFile
from pyuvs.spectra import calculate_calibration_curve, rebin_muv_wavelengths
from pyuvs import *
from scipy.integrate import quadrature
from scipy.constants import Planck, speed_of_light
from pyuvs.data_converter import L1CTxt

# Read in what I should be.
l1cp = '/media/kyle/Samsung_T5/l1ctxt/orbit03400/mvn_iuv_l1c_apoapse-orbit03400-muv_20160628T104609_v13_r01.txt'
l1c = L1CTxt(l1cp)
ref_i = l1c.reflectance[-1, -1, :] * l1c.solar_flux[-1, -1, :]

# Load in an l1b file
p = Path('/media/kyle/Samsung_T5/IUVS_data/orbit03400')
files = sorted(p.glob('*apoapse*3400*muv*.gz'))
hdul = fits.open(files[0])
file = L1bFile(files[0])

# Get info from the l1b file
binwid = hdul['binning'].data['spebinwidth'][0]
lo = hdul['binning'].data['spepixlo'][0]
hi = hdul['binning'].data['spepixlo'][0]
wav_edges = load_muv_wavelength_edges()
detector_wavs = np.concatenate((file.binning.spectral_pixel_low[0, :], np.array([818])))
wavedge = wav_edges[detector_wavs]
vg = file.observation.voltage_gain
wavs = file.observation.wavelength[0, :]
ww = np.median(file.observation.wavelength_width) * 1e-9

# Load in the calibration factor and rebin it to 19 wavs
calfactorgrid = np.genfromtxt('/home/kyle/Downloads/calibration_factor_20191024.txt')  # 0 is bin, 1 in wav, 2 is factor
fact = calfactorgrid[:, 2]
calfactor = np.array([np.mean(fact[detector_wavs[i]: detector_wavs[i+1]]) for i in range(19)])
calfactor = np.broadcast_to(calfactor, (133, 19))
volt_correction = 2.925 - 0.0045167*vg + 2.7333e-6*vg**2

# correct the IUVS data
ff = load_flatfield_mid_hi_res_pipeline()
primary = file.detector_image.calibrated
primary = primary * calfactor * volt_correction / ff
iuvs_i = primary[-1, -1, :]
sza = file.pixel_geometry.solar_zenith_angle[-1, -1]

# ref_i is 1.7025 time larger than iuvs_i. the sza and mars-sun distance
# don't change things.

# Get the solar spectrum
sspath = '/home/kyle/solar/solar_flux_solstice_muv_201606.txt'
ss = np.genfromtxt(sspath)  # 0 is wav, 1 is spectrum, 2 is unc

# Get the solar flux
def solar(wav):
    return np.interp(wav, ss[:, 0], ss[:, 1])


def integrate_solar(low, high):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return quadrature(solar, low, high)[0]


# Convert solar flux to kR/nm
ss[:, 1] = ss[:, 1] * 1e-12 / (Planck * speed_of_light) * 1e-4 * 1e4*1e-10 * 4 * np.pi / 1000

intsolar = np.array([integrate_solar(wavedge[i], wavedge[i+1]) for i in range(len(wavs))])
intsolar = intsolar / (1.5**2)
print(intsolar / 0.159*6421)

#l1cp = '/media/kyle/Samsung_T5/l1ctxt/orbit03400/mvn_iuv_l1c_apoapse-orbit03400-muv_20160628T104609_v13_r01.txt'





