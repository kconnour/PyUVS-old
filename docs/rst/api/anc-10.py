import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pyuvs as pu

fig, ax = plt.subplots(1, 1, figsize=(6, 3), constrained_layout=True)

b_field = pu.anc.load_map_magnetic_field_closed_probability()
ax.imshow(b_field, cmap='Blues_r', extent=[0, 360, -90, 90], origin='lower', rasterized=True)
ax.set_xlabel('Longitude [degrees]')
ax.set_ylabel('Latitude [degrees]')
ax.xaxis.set_major_locator(ticker.MultipleLocator(30))
ax.yaxis.set_major_locator(ticker.MultipleLocator(30))

plt.show()