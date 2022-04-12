from pathlib import Path
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from pyuvs.data_converter import L1CTxt
from pyuvs.datafiles import L1bFile
import warnings
from pyuvs import *
from scipy.constants import Planck, speed_of_light
from scipy.integrate import quadrature

fig, ax = plt.subplots(1, 14, figsize=(14, 2))


# Read in Franck's numbers
l1cp = '/media/kyle/Samsung_T5/l1ctxt/orbit03400/mvn_iuv_l1c_apoapse-orbit03400-muv_20160628T104609_v13_r01.txt'
l1c = L1CTxt(l1cp)

# Load in an l1b file
p = Path('/media/kyle/Samsung_T5/IUVS_data/orbit03400')
files = sorted(p.glob('*apoapse*3400*muv*.gz'))
hdul = fits.open(files[0])
file = L1bFile(files[0])

spectral_bin_width = hdul['binning'].data['spebinwidth'][0]
spectral_low = hdul['binning'].data['spepixlo'][0]
spectral_high = hdul['binning'].data['spepixhi'][0]


# Read in wavelengths
refhdul = fits.open('/media/kyle/Samsung_T5/IUVS_data/orbit03300/mvn_iuv_l1b_periapse-orbit03334-muv_20160616T054624_v13_r01.fits.gz')
for foobar in range(3):
    if foobar == 0:
        # Read in the bin offset for the first integration
        binoffset = np.load('/home/kyle/ql_testing/binoffset.npy')
    elif foobar == 1:
        binoffset = np.load('/home/kyle/ql_testing/binoffset084.npy')
    elif foobar == 2:
        binoffset = np.load('/home/kyle/ql_testing/binoffset092.npy')
    print(binoffset)

    for counter, asdf in enumerate(binoffset):
        print(counter)
        muv_wavelength_centers = refhdul['observation'].data['wavelength'][0, 0, :] + asdf * 0.16535
        median_diff = np.abs(np.median(np.diff(muv_wavelength_centers)))
        muv_wavelength_edges = np.concatenate((muv_wavelength_centers - median_diff/2, np.array([muv_wavelength_centers[-1] + median_diff/2])))

        # Get info from the l1b file and outside sources
        detector_ww_width = np.mean(np.abs(np.diff(muv_wavelength_edges)))

        binned_low_wavs = np.concatenate((file.binning.spectral_pixel_low[0, :], np.array([818])))
        binned_wavelength_edges = muv_wavelength_edges[binned_low_wavs]
        binned_wavelength_centers = file.observation.wavelength[0, :]
        voltage = file.observation.voltage
        binned_wavelength_width = np.median(file.observation.wavelength_width)
        psf = load_muv_point_spread_function()

        # Load in the calibration factor and rebin it to 19 wavs
        calfactorgrid = np.genfromtxt('/home/kyle/Downloads/calibration_factor_20191024.txt')  # 0 is bin, 1 in wav, 2 is factor
        calfactor = calfactorgrid[:, 2]

        # Rebin the calibration factor to the real wavelengths
        calfactor = np.array([np.mean(calfactor[binned_low_wavs[i]: binned_low_wavs[i+1]]) for i in range(19)])
        volt_correction = 2.925 - 0.0045167*voltage + 2.7333e-6*voltage**2

        # Correct the IUVS data and convert it to kR---not kR/nm
        ff = load_flatfield_mid_hi_res_pipeline()
        primary = hdul['primary'].data
        primary = primary * calfactor / ff * binned_wavelength_width * volt_correction

        # Load in the solar spectrum
        solstice = np.genfromtxt('/home/kyle/solar/solsticev18/solar_flux_solstice_muv_201606.txt')   # 0 is wav (nm), 1 is flux in W/m2/nm

        # Turn the flux into kR
        solar_flux = solstice[:, 1] * 1e-9 / (Planck * speed_of_light) * 4 * np.pi * 1e-10 * solstice[:, 0] / 1000


        # Get the solar flux
        def solar(wav):
            return np.interp(wav, solstice[:, 0], solar_flux)


        def integrate_solar(low, high):
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                return quadrature(solar, low, high)[0]


        # Integrate the solar flux / rebin it to 1024 bin
        intsolar = np.array([integrate_solar(muv_wavelength_edges[i], muv_wavelength_edges[i+1]) for i in range(1024)])
        # Divide the flux by 1/R**2
        intsolar *= 1 / 1.4738**2

        # Convolve the flux by the PSF
        convolved_flux = np.convolve(intsolar, psf, mode='same')
        rebinned_solar_flux = np.array([np.sum(convolved_flux[binned_low_wavs[i]: binned_low_wavs[i+1]]) for i in range(19)])

        # Make I/F
        sza = np.tile(hdul['pixelgeometry'].data['pixel_solar_zenith_angle'][..., None], 19)
        reflectance = primary * np.pi / np.cos(np.radians(sza)) / rebinned_solar_flux

        if counter % 10 == 0:
            if foobar == 0:
                ax[counter//10].plot(binned_wavelength_centers, l1c.reflectance[-1, counter, :], label='original (0.89 shift)')
                ax[counter//10].plot(binned_wavelength_centers, reflectance[-1, counter, :], label='corrected')
            elif foobar == 1:
                ax[counter // 10].plot(binned_wavelength_centers, reflectance[-1, counter, :], color='g', label='0.84 shift')
            elif foobar == 2:
                ax[counter // 10].plot(binned_wavelength_centers, reflectance[-1, counter, :], color='r', label='0.92 shift')

plt.savefig('/home/kyle/ql_testing/spec_corr0.png')
