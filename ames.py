from netCDF4 import Dataset
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import matplotlib as mpl
'''
rmars = 3400

# Diurn plev is the last Ames description
gcm = Dataset('/home/kyle/ames/sim1/c48_big.atmos_diurn_plev-002.nc', "r", format='NETCDF4')

print(gcm.variables)

#lon = gcm.variables['lon']
clouds = gcm.variables['cldcol']
clouds = np.roll(clouds, 90, axis=-1)   # cartopy needs longitudes from -180 to + 180

fig = plt.figure(figsize=(6, 6), facecolor='k')
globe = ccrs.Globe(semimajor_axis=rmars * 1e3, semiminor_axis=rmars * 1e3)
projection = ccrs.NearsidePerspective(central_latitude=-11.444, central_longitude=241.25,
                                      satellite_height=6061.5*10**3, globe=globe)


for i in range(24):
    fig = plt.figure(figsize=(6, 6), facecolor='w')
    globe_ax = plt.axes(projection=projection)

    lat = np.linspace(-90, 90, num=91)
    lon = np.linspace(-180, 180, num=181)

    im = globe_ax.pcolormesh(lon, lat, clouds[int(377/668 * 70), i, :, :], transform=ccrs.PlateCarree(globe=globe), vmin=0, vmax=0.001)

    plt.savefig(f'/home/kyle/ames/graphics/3464-{i}.png')
    plt.close(fig)'''

fig = plt.figure()
ax = fig.add_axes([0.475, 0.05, 0.05, 0.9])

cb = mpl.colorbar.ColorbarBase(ax, orientation='vertical',
                               cmap='viridis', norm=mpl.colors.Normalize(0, 0.001), ticks = [0, 0.00025, 0.0005, 0.00075, 0.001])

plt.savefig(f'/home/kyle/ames/graphics/3464colorbar')
