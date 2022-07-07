from datetime import date
import glob
import math
from pathlib import Path
import warnings

from astropy.io import fits
import numpy as np
import psycopg
from scipy.constants import Planck, speed_of_light
from scipy.integrate import quadrature
from scipy.io import readsav

from pyuvs import load_muv_sensitivity_curve_observational, pixel_omega, \
    load_flatfield_mid_res_app_flip, load_muv_point_spread_function


orbit = 16308
p = Path('/media/kyle/McDataFace/iuvsdata/stage/orbit16300')
files = sorted(p.glob(f'*apoapse*{orbit}*muv*s02*.gz'))
for fileno in range(10):
    # Open the .fits file and read in relevant data
    hdul = fits.open(files[fileno])
    primary = hdul['primary'].data
    dds = hdul['detector_dark_subtracted'].data
    sza = hdul['pixelgeometry'].data['pixel_solar_zenith_angle']
    spectral_bin_width: int = int(np.median(hdul['binning'].data['spebinwidth'][0]))  # bins
    spatial_bin_width: int = int(np.median(hdul['binning'].data['spabinwidth'][0]))  # bins
    #starting_spectral_index = hdul['binning'].data['spebinwidth'][0][0] / spectral_bin_width
    spectral_bin_low = hdul['binning'].data['spepixlo'][0, :]  # bin number
    spectral_bin_high = hdul['binning'].data['spepixhi'][0, :]  # bin number
    voltage: float = hdul['observation'].data['mcp_volt'][0]
    voltage_gain: float = hdul['observation'].data['mcp_gain'][0]
    integration_time: float = hdul['observation'].data['int_time'][0]

    # Make the voltage correction
    volt_correction = 2.925 - 0.0045167 * voltage + 2.7333e-6 * voltage ** 2

    # Read in Justin's wavelengths
    justins_files = sorted(glob.glob(f'/home/kyle/iuvs/wavelengths/broken-spacecraft-nonlin-edges/*orbit{orbit}*.sav'))
    wavelength_center = readsav(justins_files[fileno])['wavelength_muv']  # shape: (50, 20)
    wavelength_low = readsav(justins_files[fileno])['wavelength_muv_lo']
    wavelength_high = readsav(justins_files[fileno])['wavelength_muv_hi']

    # Make wavelength edges from these data
    wavelength_edges = np.zeros((wavelength_low.shape[0], wavelength_low.shape[1]+1))
    wavelength_edges[:, :-1] = wavelength_low
    wavelength_edges[:, -1] = wavelength_high[:, -1]
    spectral_bin_edges = np.concatenate((spectral_bin_low, np.array([spectral_bin_high[-1]])))

    # Don't trust the primary structure--do it myself. This will make kR, not kR/nm
    sensitivity_curve = load_muv_sensitivity_curve_observational()   # shape: (512, 2)
    rebinned_sensitivity_curve = np.interp(wavelength_center, sensitivity_curve[:, 0], sensitivity_curve[:, 1]) # shape: wavelength_center.shape
    rebinned_calibration_curve = voltage_gain * integration_time * rebinned_sensitivity_curve * pixel_omega * spatial_bin_width * 10**9 / (4 * np.pi)
    kR = dds / rebinned_calibration_curve

    # Query the db
    with psycopg.connect(host='localhost', dbname='iuvs', user='kyle',
                         password='iuvs') as connection:
        # Open a cursor for db operations
        with connection.cursor() as cursor:
            cursor.execute(
                f"select solar_distance, utc from apoapse where orbit = {orbit}")
            a = cursor.fetchall()

    # Compute the Mars radius ratio
    orb_dist_earth = 1.496e8
    orb_dist_mars = a[0][0]
    radius = orb_dist_mars / orb_dist_earth

    # Get the year and month of the orbit for the solar flux computation
    dt = a[0][1]

    if dt.year >= 2020 and dt.month > 2:
        # raise SystemExit('The orbit does not have a corresponding solar flux')
        dt = date(2019, dt.month, 1)

    # Format the stuff for Franck's solstice naming convention
    month = f'{dt.month}'.zfill(2)
    yearmonth = f'{dt.year}{month}'

    # Make the orbit code
    code = 'orbit' + f'{math.floor(orbit / 100) * 100}'.zfill(5)

    # Load in the flatfield
    flatfield = load_flatfield_mid_res_app_flip()

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


    # Make a reflectance array that I'll populate. Then populate it
    reflectance = np.zeros(kR.shape)
    for spabin in range(reflectance.shape[1]):
        # Compute the wavelengths on a 1024 grid (but don't take all 1024 pixels since some are in the keyholes)
        pixel_edges = np.arange(spectral_bin_edges[0], spectral_bin_edges[-1] + 1)
        pixel_edge_wavelengths = np.interp(pixel_edges, spectral_bin_edges, wavelength_edges[spabin, :])

        # Integrate the solar flux / rebin it to the number of spectral bins used in the observation
        intsolar = np.array([integrate_solar(pixel_edge_wavelengths[i], pixel_edge_wavelengths[i+1]) for i in range(len(pixel_edge_wavelengths)-1)])

        # Divide the flux by 1/R**2
        intsolar *= 1 / radius ** 2

        # Convolve the flux by the PSF
        convolved_flux = np.convolve(intsolar, psf, mode='same')
        edge_indices = spectral_bin_edges - spectral_bin_edges[0]

        rebinned_solar_flux = np.array([np.sum(convolved_flux[edge_indices[i]: edge_indices[i+1]]) for i in range(reflectance.shape[2])])

        for integration in range(reflectance.shape[0]):
            kR[integration, spabin, :19] = kR[integration, spabin, :19] / flatfield[spabin, :] * volt_correction
            reflectance[integration, spabin, :19] = kR[integration, spabin, :19] * np.pi / np.cos(np.radians(sza[integration, spabin])) / rebinned_solar_flux[..., :19]

    # Save the reflectance
    print(np.amax(reflectance), np.amin(reflectance))
    np.save(f'/home/kyle/iuvs/reflectance/{code}/reflectance{orbit}-{fileno}-nonlinear.npy', reflectance)
