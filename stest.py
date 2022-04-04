import numpy as np
from scipy.constants import Planck, speed_of_light
from pathlib import Path
from astropy.io import fits
from pyuvs import *
from pyuvs.datafiles import L1bFile
from scipy.integrate import quadrature
import warnings
from pyuvs.data_converter import L1CTxt
import matplotlib.pyplot as plt

# Read in Franck's numbers
l1cp = '/media/kyle/Samsung_T5/l1ctxt/orbit03400/mvn_iuv_l1c_apoapse-orbit03400-muv_20160628T104609_v13_r01.txt'
l1c = L1CTxt(l1cp)

# Load in the hires solar spectrum
foo = np.genfromtxt('/home/kyle/solar/atlas3_thuillier_tuv.txt', skip_header=9)  # 0 is wav (nm), 1 is flux

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
detector_ww_width = np.mean(np.abs(np.diff(wav_edges)))
detector_wavs = np.concatenate((file.binning.spectral_pixel_low[0, :], np.array([818])))
wavedge = wav_edges[detector_wavs]
vg = file.observation.voltage_gain
wavs = file.observation.wavelength[0, :]
ww = np.median(file.observation.wavelength_width) * 1e-9


# Convert the solar spectrum to kR/nm
factor = foo[:, 0] * 1e-12 / (Planck * speed_of_light) * 1e-4
foo[:, 1] = foo[:, 1] * factor * 1e4 * 1e-10 * 4 * np.pi / 1000


# Get the solar flux
def solar(wav):
    return np.interp(wav, foo[:, 0], foo[:, 1])


def integrate_solar(low, high):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return quadrature(solar, low, high)[0]


# Integrate the solar flux / rebin it to 1024 bin
intsolar = np.array([integrate_solar(wav_edges[i], wav_edges[i+1]) for i in range(len(wav_edges)-1)]) / detector_ww_width

plt.plot(wav_edges[:-1], intsolar)

foo = np.genfromtxt('/home/kyle/solar/solar_flux_solstice_muv_201606.txt')
foo[:, 1] = foo[:, 1] * 1e3

# Convert the solar spectrum to kR/nm
factor = foo[:, 0] * 1e-12 / (Planck * speed_of_light) * 1e-4
foo[:, 1] = foo[:, 1] * factor * 1e4 * 1e-10 * 4 * np.pi / 1000

# Integrate the solar flux / rebin it to 1024 bin
intsolar = np.array([integrate_solar(wav_edges[i], wav_edges[i+1]) for i in range(len(wav_edges)-1)]) / detector_ww_width

plt.plot(wav_edges[:-1], intsolar)
plt.savefig('/home/kyle/ql_testing.fuckthis.png')