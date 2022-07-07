from datetime import date
import glob
import math
from pathlib import Path

from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import psycopg
from scipy.io import readsav

from pyuvs import load_muv_sensitivity_curve_observational, pixel_omega


orbit = 16407
fileno = 8
p = Path('/media/kyle/McDataFace/iuvsdata/stage/orbit16400')
files = sorted(p.glob(f'*apoapse*{orbit}*muv*s02*.gz'))

# Open the .fits file and read in relevant data
hdul = fits.open(files[fileno])
hdul.info()
primary = hdul['primary'].data
dds = hdul['detector_dark_subtracted'].data
sza = hdul['pixelgeometry'].data['pixel_solar_zenith_angle']
#spectral_bin_width: int = int(np.median(hdul['binning'].data['spebinwidth'][0]))  # bins
spatial_bin_width: int = int(np.median(hdul['binning'].data['spabinwidth'][0]))  # bins
#starting_spectral_index = hdul['binning'].data['spebinwidth'][0][0] / spectral_bin_width
#spectral_bin_low = hdul['binning'].data['spepixlo'][0, :19]  # bin number
#spectral_bin_high = hdul['binning'].data['spepixhi'][0, :19]  # bin number
voltage_gain: float = hdul['observation'].data['mcp_gain'][0]
integration_time: float = hdul['observation'].data['int_time'][0]

# Read in Justin's wavelengths
files = sorted(glob.glob(f'/home/kyle/iuvs/wavelengths/broken-spacecraft-nonlin-edges/*orbit{orbit}*.sav'))
wavelength_center = readsav(files[fileno])['wavelength_muv']  # shape: (50, 20)
wavelength_low = readsav(files[fileno])['wavelength_muv_lo']
wavelength_high = readsav(files[fileno])['wavelength_muv_hi']

# DON'T trust the primary structure---do it myself. This will make kR, not kR/nm
sensitivity_curve = load_muv_sensitivity_curve_observational()   # shape: (512, 2)
rebinned_sensitivity_curve = np.interp(wavelength_center, sensitivity_curve[:, 0], sensitivity_curve[:, 1]) # shape: wavelength_center.shape
rebinned_calibration_curve = voltage_gain * integration_time * rebinned_sensitivity_curve * pixel_omega * spatial_bin_width * 10**9 / (4 * np.pi)
kR = dds / rebinned_calibration_curve

# Query the db
with psycopg.connect(host='localhost', dbname='iuvs', user='kyle',
                     password='iuvs') as connection:
    # I still need Mars year, Sol
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

