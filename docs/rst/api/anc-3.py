import matplotlib.pyplot as plt
import pyuvs as pu

fig, ax = plt.subplots()

flatfield = pu.load_flatfield_hi_res()
ax.imshow(flatfield.T, cmap='inferno')
ax.set_xlabel('Spatial bin')
ax.set_ylabel('Spectral bin')
plt.show()