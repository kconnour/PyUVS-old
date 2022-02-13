import matplotlib.pyplot as plt
import pyuvs as pu

fig, ax = plt.subplots(1, 1, figsize=(8, 2), constrained_layout=True)

flatfield = pu.load_flatfield_mid_hi_res_my34gds()
ax.pcolormesh(flatfield.T, cmap='inferno', rasterized=True)
ax.set_xlabel('Spatial bin')
ax.set_ylabel('Spectral bin')

plt.show()