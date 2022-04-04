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

lamtrue = np.zeros((10000,))
fluxtrue = np.zeros((10000,))

# NOTE: this file has 1024 spectral binning and it agrees with Franck
refhdul = fits.open('/media/kyle/Samsung_T5/IUVS_data/orbit03300/mvn_iuv_l1b_periapse-orbit03334-muv_20160616T054624_v13_r01.fits.gz')
muv_wavelength_centers = refhdul['observation'].data['wavelength'][0, 0, :]
median_diff = np.abs(np.median(np.diff(muv_wavelength_centers)))
muv_wavelength_edges = np.concatenate((muv_wavelength_centers - median_diff/2, np.array([muv_wavelength_centers[-1] + median_diff/2])))

# Load in an l1b file
p = Path('/media/kyle/Samsung_T5/IUVS_data/orbit03400')
files = sorted(p.glob('*apoapse*3400*muv*.gz'))
print(files[0])
hdul = fits.open(files[0])
file = L1bFile(files[0])

# Get info from the l1b file and outside sources
spatial_bin_width = hdul['binning'].data['spabinwidth'][0]
spectral_bin_width = hdul['binning'].data['spebinwidth'][0]
median_spa_bin_width = int(np.median(spatial_bin_width))
median_spe_bin_width = int(np.median(spectral_bin_width))

spatial_low = hdul['binning'].data['spapixlo'][0]
spatial_high = hdul['binning'].data['spapixhi'][0]

spectral_low = hdul['binning'].data['spepixlo'][0]
spectral_high = hdul['binning'].data['spepixhi'][0]
detector_wavelength_width = np.mean(np.abs(np.diff(muv_wavelength_edges)))

binned_low_wavs = np.concatenate((file.binning.spectral_pixel_low[0, :], np.array([818])))
binned_wavelength_edges = muv_wavelength_edges[binned_low_wavs]
spatial_bins_pixel = np.abs(np.median(np.diff(spectral_low)))
binned_wavelength_centers = file.observation.wavelength[0, :]
voltage = file.observation.voltage
binned_wavelength_width = np.median(file.observation.wavelength_width)
psf = load_muv_point_spread_function()

# Load in the calibration factor
calfactorgrid = np.genfromtxt('/home/kyle/Downloads/calibration_factor_20191024.txt')  # 0 is bin, 1 in wav, 2 is factor
calfactor = calfactorgrid[:, 2]

# apply the calibration factor. I think this is what Franck did but more compactly
calfactor = np.array([np.mean(calfactor[binned_low_wavs[i]: binned_low_wavs[i+1]]) for i in range(19)])
volt_correction = 2.925 - 0.0045167*voltage + 2.7333e-6*voltage**2

# Correct the IUVS data and convert it to kR---not kR/nm
ff = load_flatfield_mid_hi_res_pipeline()
primary = hdul['primary'].data
primary = primary * calfactor * ff * binned_wavelength_width * volt_correction

# Load in the solar spectrum
iss = np.genfromtxt('/home/kyle/solar/solar-iss_v1.1.txt', skip_header=16)   # 0 is wav (nm), 1 is flux in W/m2/nm
solstice = np.genfromtxt('/home/kyle/solar/solsticev17/solar_flux_solstice_muv_201606.txt')   # 0 is wav (nm), 1 is flux in W/m2/nm
solstice_wavs = solstice[:, 0]

lines = 0
for i in range(10000):
    if iss[i, 0] < 180.5:
        lamtrue[lines] = iss[i, 0]
        fluxtrue[lines] = iss[i, 1]
        lines += 1

for i in range(130):
    lamtrue[lines] = solstice_wavs[i]
    fluxtrue[lines] = solstice[i, 1]
    lines += 1

for i in range(10000):
    if iss[i, 0] > 309.5:
        lamtrue[lines] = iss[i, 0]
        fluxtrue[lines] = iss[i, 1]
        lines += 1

# Turn the flux into kR
solar_flux = solstice[:, 1] * 1e-9 / (Planck * speed_of_light) * 4 * np.pi * 1e-10 * solstice[:, 0] / 1000
fluxtrue = fluxtrue * 1e-9 / (Planck * speed_of_light) * 4 * np.pi * 1e-10 * lamtrue / 1000


# Get the solar flux
def solar(wav):
    return np.interp(wav, solstice[:, 0], solar_flux)


def integrate_solar(low, high):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return quadrature(solar, low, high)[0]


# Do the 1024 rebinning Franck's way
'''
# This was franck's code from an old .f file
fuck = np.zeros((1024,))
for i in range(1024):
    cpt = 0
    for j in range(len(solar_flux)):
        if muv_wavelength_edges[i] <= solstice_wavs[j] <= muv_wavelength_edges[i+1]:
            cpt = cpt + 1
            fuck[i] = fuck[i] + solar_flux[j]
    if cpt > 0:
        fuck[i] = fuck[i] / cpt'''
fuck = np.zeros((1024,))
for i in range(1024):
    cpt = 0
    '''for j in range(1, len(solar_flux)-1):
        deltam = solstice_wavs[j] - solstice_wavs[j-1]
        deltap = solstice_wavs[j+1] - solstice_wavs[j]
        if (muv_wavelength_centers[i] >= solstice_wavs[j] - deltam/2) and (muv_wavelength_centers[i] <= solstice_wavs[j] + deltap/2) :
            cpt = cpt + 1
            fuck[i] = fuck[i] + solar_flux[j]'''
    for j in range(1, 9999):
        deltam = lamtrue[j] - lamtrue[j-1]
        deltap = lamtrue[j+1] - lamtrue[j]
        if (muv_wavelength_centers[i] >= lamtrue[j-1] - deltam/2) and (muv_wavelength_centers[i] <= lamtrue[j-1] + deltap/2) :
            cpt = cpt + 1
            fuck[i] = fuck[i] + fluxtrue[j-1]
    if cpt > 0:
        fuck[i] = fuck[i] / cpt
    #else:
    #    fuck[i] = 1e30


intsolar = np.array([integrate_solar(muv_wavelength_edges[i], muv_wavelength_edges[i+1]) for i in range(1024)])
'''print(fuck)
print(intsolar)
plt.plot(fuck / intsolar)
plt.axvline(spectral_low[1])
plt.axvline(spectral_low[-1])
plt.ylim(5, 7)
plt.savefig('/home/kyle/ql_testing/diffsolarratio.png')
raise SystemExit(9)'''


convolved_flux = np.convolve(fuck, psf)
convolved_flux *= (1/1.4738**2)

# Do the rebinning Franck's way
'''foobar = np.zeros((primary.shape[1], primary.shape[2]))
for i in range(133):
    for j in range(19):
        sum = 0
        medspecbinwidth = int(np.median(spectral_bin_width))
        for k in range(medspecbinwidth):
            l = spectral_low[0] + k + (j * medspecbinwidth)
            sum = sum + convolved_flux[l]
        foobar[i, j] = sum / medspecbinwidth'''

# Or do the rebinning my way. They are identical.
rebinned_solar_flux = np.array([np.sum(convolved_flux[binned_low_wavs[i]: binned_low_wavs[i+1]]) for i in range(19)]) * detector_wavelength_width
#print(rebinned_solar_flux)
#print(foobar[-1, :] * binned_wavelength_width)

# Make I/F
sza = np.tile(hdul['pixelgeometry'].data['pixel_solar_zenith_angle'][..., None], 19)
reflectance = primary * np.pi / np.cos(np.radians(sza)) / rebinned_solar_flux
print(reflectance[-1, -1, :])

# Franck's rebin, my convolution
convolved_flux0 = np.convolve(fuck, psf, mode='same')
convolved_flux0 *= (1/1.4738**2)
rebinned_solar_flux0 = np.array([np.sum(convolved_flux0[binned_low_wavs[i]: binned_low_wavs[i+1]]) for i in range(19)]) * detector_wavelength_width
reflectance0 = primary * np.pi / np.cos(np.radians(sza)) / rebinned_solar_flux0
print(reflectance0[-1, -1, :])

# My rebin, my convolution
convolved_flux1 = np.convolve(intsolar, psf, mode='same')
convolved_flux1 *= (1/1.4738**2)
rebinned_solar_flux1 = np.array([np.sum(convolved_flux1[binned_low_wavs[i]: binned_low_wavs[i+1]]) for i in range(19)])
reflectance1 = primary * np.pi / np.cos(np.radians(sza)) / rebinned_solar_flux1
print(reflectance1[-1, -1, :])

plt.plot(binned_wavelength_centers, l1c.reflectance[-1, -1, :], label='original')
plt.plot(binned_wavelength_centers, reflectance[-1, -1, :], label='franck-method')
plt.plot(binned_wavelength_centers, reflectance1[-1, -1, :], label='kyle')
plt.legend()
plt.savefig('/home/kyle/ql_testing/s18spectra.png')
