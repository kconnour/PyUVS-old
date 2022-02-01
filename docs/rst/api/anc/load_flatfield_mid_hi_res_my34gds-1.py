import matplotlib.pyplot as plt
import pyuvs as pu

fig, ax = plt.subplots(figsize=(6, 2))

flatfield = pu.load_flatfield_mid_hi_res_my34gds()
ax.imshow(flatfield.T, cmap='inferno')
ax.set_xlabel('Spatial bin')
ax.set_ylabel('Spectral bin')
plt.show()