from netCDF4 import Dataset
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
from pyproj import CRS, Transformer

rmars = 3400

# Diurn plev is the last Ames description
gcm = Dataset('/home/kyle/lmd_gcm_runs/run_MY33/diagfi7.nc', "r", format='NETCDF3')

lon = gcm.variables['longitude']
lat = gcm.variables['latitude']
print(lat[:])
clouds = gcm.variables['icetot']  # time, lat, lon
lat = np.linspace(-90, 90, num=50)
lon = np.linspace(-180, 180, num=66)

fig = plt.figure(figsize=(6, 6), facecolor='w')
globe = ccrs.Globe(semimajor_axis=rmars * 1e3, semiminor_axis=rmars * 1e3)
projection = ccrs.NearsidePerspective(central_latitude=-11.444, central_longitude=241.25,
                                      satellite_height=6061.5*10**3, globe=globe)

for i in range(5):
    fig = plt.figure(figsize=(6, 6), facecolor='w')
    globe_ax = plt.axes(projection=projection)
    if i == 0:
        c = (clouds[22, :, :]*2 + clouds[23, :, :])/3
    if i == 1:
        c = clouds[23, :, :]
    if i == 2:
        c = (clouds[23, :, :]*2 + clouds[24, :, :])/3
    if i == 3:
        c = (clouds[23, :, :] + clouds[24, :, :]*2)/3
    if i == 4:
        c = clouds[24, :, :]
    globe_ax.pcolormesh(lon, lat, np.flipud(c), transform=ccrs.PlateCarree(globe=globe), vmin=0, vmax=0.001)
    plt.savefig(f'/home/kyle/lmd_gcm_runs/graphics/3464-{i}.png')
    plt.close(fig)
