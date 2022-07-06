# This script will take in a file of the wavelengths for an MUV file and make
# the I/F spectra using Justin's wavelengths
# This is the latest l1c file I have as of April 18, 2022
import math
import numpy as np
from scipy.constants import Planck, speed_of_light
from pathlib import Path
from astropy.io import fits
from pyuvs import *
from scipy.integrate import quadrature
import warnings
from scipy.io import readsav
import glob
import psycopg
from datetime import date

orbit = 16308
#fileno = 0
for fileno in range(10):

    # Do the DB query
    with psycopg.connect(host='localhost', dbname='iuvs', user='kyle', password='iuvs') as connection:
        # I still need Mars year, Sol
        # Open a cursor for db operations
        with connection.cursor() as cursor:
            cursor.execute(f"select solar_distance, utc from apoapse where orbit = {orbit}")
            a = cursor.fetchall()

    # Compute the Mars radius ratio
    orb_dist_earth = 1.496e8
    orb_dist_mars = a[0][0]
    radius = orb_dist_mars / orb_dist_earth

    # Get the year and month of the orbit for the solar flux computation
    dt = a[0][1]

    if dt.year >= 2020 and dt.month > 2:
        #raise SystemExit('The orbit does not have a corresponding solar flux')
        dt = date(2019, dt.month, 1)

    # Format the stuff for Franck's solstice naming convention
    month = f'{dt.month}'.zfill(2)
    yearmonth = f'{dt.year}{month}'

    # Make the orbit code
    code = 'orbit' + f'{math.floor(orbit/100)*100}'.zfill(5)

    # Load in an l1b file. This only works for 3D primaries!
    #p = Path(f'/media/kyle/Samsung_T5/IUVS_data/{code}')
    p = Path(f'/media/kyle/McDataFace/iuvsdata/stage/{code}')
    files = sorted(p.glob(f'*apoapse*{orbit}*muv*s02*.gz'))
    hdul = fits.open(files[fileno])
    primary = hdul['primary'].data[:, :, :19]
    sza = hdul['pixelgeometry'].data['pixel_solar_zenith_angle']
    og_wavs = hdul['observation'].data['wavelength'][0][0, :19]

    # Read in Justin's wavelengths, which are independent of integration
    # TODO: load in the proper Justin's wavelengths. It may be better to just modify the .fits file
    #files = sorted(glob.glob('/home/kyle/Downloads/mvn_iuv_wl_apoapse-orbit03464-muv/*.sav'))
    files = sorted(glob.glob(f'/home/kyle/iuvs/wavelengths/broken-spacecraft/*orbit{orbit}*.sav'))
    wavelengths_grid = readsav(files[fileno])['wavelength_muv'][:, :19]   # (133/50, 19) --- the same shape as the .fits structure
    reflectance = np.zeros(primary.shape)

    # Load in the calibration factor. The wavelengths provided here aren't correct
    calfactorgrid = np.genfromtxt('/home/kyle/Downloads/calibration_factor_20191024.txt')  # 0 is bin, 1 in wav, 2 is factor
    calfactor = calfactorgrid[:, 2]

    # Load in the flatfield
    flatfield = load_flatfield_mid_res_app_flip() #load_flatfield_mid_hi_res_update()   # (133, 19)

    # New wavelength-dependent FF
    '''new_ff = np.zeros((primary.shape[1:]))
    spatial_bins = np.arange(primary.shape[1])
    for spabin in spatial_bins:
        new_ff[spabin, :] = np.interp(wavelengths_grid[spabin, :], og_wavs, flatfield[spabin, :])
    flatfield = new_ff'''

    # Load in the point spread function
    psf = load_muv_point_spread_function()

    # Load in the solar spectrum
    solstice = np.genfromtxt(f'/home/kyle/solar/solsticev18/solar_flux_solstice_muv_{yearmonth}.txt')   # 0 is wav (nm), 1 is flux in W/m2/nm

    # Turn the flux into kR
    solar_flux = solstice[:, 1] * 1e-9 / (Planck * speed_of_light) * 4 * np.pi * 1e-10 * solstice[:, 0] / 1000


    # Get the solar flux
    def solar(wav):
        return np.interp(wav, solstice[:, 0], solar_flux)


    def integrate_solar(low, high):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            return quadrature(solar, low, high)[0]


    for position in range(reflectance.shape[1]):
        print(position)

        # Get info from the l1b file
        spectral_bin_width = hdul['binning'].data['spebinwidth'][0]
        spectral_bin_low = hdul['binning'].data['spepixlo'][0, :19]
        spectral_bin_high = hdul['binning'].data['spepixhi'][0, :19]
        voltage = hdul['observation'].data['mcp_volt'][0]

        # Make binning info
        bin_cutoffs = np.concatenate((spectral_bin_low, np.array([spectral_bin_high[-1]]) + 1))
        spectral_bin_center = (spectral_bin_low + spectral_bin_high + 1) / 2

        # Compute the wavelength edges, and make them onto a 1024 grid
        wavelength_bin_centers = wavelengths_grid[position, :]
        wavelength_bin_diff = np.median(np.abs(np.diff(wavelength_bin_centers)))
        m, b = np.polyfit(spectral_bin_center, wavelength_bin_centers, 1)
        pixel_edges = np.linspace(0, 1024, num=1025)
        wavelength_edges = m * pixel_edges + b

        # Get the mean calibration factor for the new wavelengths (19)
        mean_calfactor = np.array([np.mean(calfactor[bin_cutoffs[i]: bin_cutoffs[i+1]]) for i in range(reflectance.shape[2])])
        volt_correction = 2.925 - 0.0045167 * voltage + 2.7333e-6 * voltage ** 2

        # Integrate the solar flux / rebin it to 1024 bin
        intsolar = np.array([integrate_solar(wavelength_edges[i], wavelength_edges[i+1]) for i in range(1024)])

        # Divide the flux by 1/R**2
        intsolar *= 1 / radius**2

        # Convolve the flux by the PSF
        convolved_flux = np.convolve(intsolar, psf, mode='same')
        rebinned_solar_flux = np.array([np.sum(convolved_flux[bin_cutoffs[i]: bin_cutoffs[i+1]]) for i in range(reflectance.shape[2])])

        for integration in range(reflectance.shape[0]):
            # Correct the IUVS data and convert it to kR---not kR/nm
            primary[integration, position, :] = primary[integration, position, :] * mean_calfactor / flatfield[position, :] * wavelength_bin_diff * volt_correction
            reflectance[integration, position, :] = primary[integration, position, :] * np.pi / np.cos(np.radians(sza[integration, position])) / rebinned_solar_flux


    # Save the reflectance
    print(np.amax(reflectance), np.amin(reflectance))
    np.save(f'/home/kyle/iuvs/reflectance/orbit16300/reflectance{orbit}-{fileno}-linear.npy', reflectance)
