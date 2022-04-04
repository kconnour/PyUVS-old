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

# Read in the calibration factor
calfactorgrid = np.genfromtxt('/home/kyle/Downloads/calibration_factor_20191024.txt')  # 0 is bin, 1 in wav, 2 is factor
franckwavdelta = 0.16535
franckwavedges = np.concatenate((calfactorgrid[:, 1] - franckwavdelta / 2, np.array([calfactorgrid[-1, 1] + franckwavdelta/ 2])))

# Load in the hires or SOLSTICE solar spectrum
#foo = np.genfromtxt('/home/kyle/solar/atlas3_thuillier_tuv.txt', skip_header=9)  # 0 is wav (nm), 1 is flux
foo = np.genfromtxt('/home/kyle/solar/solar_flux_solstice_muv_201606.txt')   # 0 is wav (nm), 1 is flux
foo[:, 1] = foo[:, 1]

# Load in an l1b file
p = Path('/media/kyle/Samsung_T5/IUVS_data/orbit03400')
files = sorted(p.glob('*apoapse*3400*muv*.gz'))
print(files[0])
hdul = fits.open(files[0])
file = L1bFile(files[0])

# Get info from the l1b file
binwid = hdul['binning'].data['spebinwidth'][0]
lo = hdul['binning'].data['spepixlo'][0]
hi = hdul['binning'].data['spepixhi'][0]
wav_edges = load_muv_wavelength_edges()
detector_ww_width = np.mean(np.abs(np.diff(wav_edges)))
binned_low_wavs = np.concatenate((file.binning.spectral_pixel_low[0, :], np.array([818])))
wavedge = wav_edges[binned_low_wavs]
vg = file.observation.voltage_gain
wavs = file.observation.wavelength[0, :]
ww = np.median(file.observation.wavelength_width)

# Convert the solar spectrum to kR/nm
factor = foo[:, 0] * 1e-9 / (Planck * speed_of_light) * 1e-4
foo[:, 1] = foo[:, 1] * factor * 1e4 * 1e-10 * 4 * np.pi / 1000


# Get the solar flux
def solar(wav):
    return np.interp(wav, foo[:, 0], foo[:, 1])


def integrate_solar(low, high):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return quadrature(solar, low, high)[0]


# Integrate the solar flux / rebin it to 1024 bin
intsolar = np.array([integrate_solar(wav_edges[i], wav_edges[i+1]) for i in range(len(wav_edges)-1)]) * detector_ww_width
intsolar *= 1 / 1.4738**2
psf = load_muv_point_spread_function()

# Do the 1024 rebinning Franck's way
fuck = np.zeros((1024,))
for i in range(1024):
    cpt = 0
    lamb = calfactorgrid[i, 1]
    for j in range(len(foo[:, 0])):
        if (foo[j, 0] >= lamb - franckwavdelta / 2) and (foo[j, 0] <= lamb + franckwavdelta / 2):
            cpt = cpt + 1
            fuck[i] = fuck[i] + foo[j, 1]
    if cpt > 0:
        fuck[i] = fuck[i] / cpt

fuck *= (1/1.4738**2)
fuck *= franckwavdelta


# Franck's method gives almost what numpy gives but is ~2% lower
def franckconvolve(arr1024):
    answer = np.zeros((1024,))
    for i in range(1024):
        for j in range(181):
            k = int(i - 90 - 1 + j)
            if k >= 0 and k <= 1024:
                try:
                    answer[i] = answer[i] + arr1024[k] * psf[j]
                except IndexError:
                    continue
    return answer


ans0 = franckconvolve(fuck)
ans1 = franckconvolve(intsolar)
ans2 = np.convolve(fuck, psf, mode='same')
ans3 = np.convolve(intsolar, psf, mode='same')
print(np.array([np.sum(ans0[binned_low_wavs[i]: binned_low_wavs[i+1]]) for i in range(19)]))
print(np.array([np.sum(ans1[binned_low_wavs[i]: binned_low_wavs[i+1]]) for i in range(19)]))
print(np.array([np.sum(ans2[binned_low_wavs[i]: binned_low_wavs[i+1]]) for i in range(19)]))
print(np.array([np.sum(ans3[binned_low_wavs[i]: binned_low_wavs[i+1]]) for i in range(19)]))

total = np.array([np.sum(ans3[binned_low_wavs[i]: binned_low_wavs[i+1]]) for i in range(19)])
print(total)
print(total / l1c.solar_flux[-1, -1, :])

ans = np.convolve(intsolar, psf, mode='same')   # idk how numpy knows, but without mode='same' it returns a 1024+181-1 shaped array
#totalflux = np.array([np.sum(ans[binned_low_wavs[i]: binned_low_wavs[i+1]]) for i in range(19)])

totalflux = np.array([np.sum(ans3[binned_low_wavs[i]: binned_low_wavs[i+1]]) for i in range(19)])
print(totalflux)
print(totalflux / l1c.solar_flux[-1, -1, :])

# Load in the calibration factor and rebin it to 19 wavs
calfactorgrid = np.genfromtxt('/home/kyle/Downloads/calibration_factor_20191024.txt')  # 0 is bin, 1 in wav, 2 is factor
fact = calfactorgrid[:, 2]
calfactor = np.array([np.mean(fact[binned_low_wavs[i]: binned_low_wavs[i+1]]) for i in range(19)])
calfactor = np.broadcast_to(calfactor, (133, 19))
volt_correction = 2.925 - 0.0045167*vg + 2.7333e-6*vg**2

# correct the IUVS data
ff = load_flatfield_mid_hi_res_pipeline()
primary = file.detector_image.calibrated
primary = primary * calfactor * volt_correction / ff
iuvs_i = primary[-1, -1, :]
sza = file.pixel_geometry.solar_zenith_angle[-1, -1]

totalfinalanswer = iuvs_i / totalflux / np.cos(np.radians(sza))
print(totalfinalanswer)
print(l1c.reflectance[-1, -1, :] / totalfinalanswer)

w = np.linspace(205, 306, num=19)
plt.plot(w, totalfinalanswer, label='kyle')
plt.plot(w, l1c.reflectance[-1, -1, :], label='franck')
plt.legend()
plt.savefig('/home/kyle/ql_testing/refscaled2.png')
