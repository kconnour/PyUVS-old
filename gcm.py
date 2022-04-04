from scipy.io import netcdf_file
import matplotlib.pyplot as plt
import numpy as np

file = netcdf_file('/home/kyle/lmd_gcm_runs/run_MY33/diagfi7.nc', 'r')

time = file.variables['Time'][:]
lat = file.variables['latitude'][:]
lon = file.variables['longitude'][:]
ice = file.variables['icetot'][:]
dust = file.variables['dustq'][:]

sdust = np.sum(dust[24, :, 15:35, 10:30], axis=0)

fig, ax = plt.subplots(1, 2)

ax[0].imshow(ice[24, 19:23, 20:25], vmin=0, vmax=0.005)
ax[1].imshow(sdust, vmin=0)

plt.savefig('/home/kyle/ql_testing/gcm.png')

file.close()
