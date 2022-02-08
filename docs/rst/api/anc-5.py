import matplotlib.pyplot as plt
import pyuvs as pu

fig, ax = plt.subplots()

flatfield = pu.load_flatfield_mid_res_no_app_flip()
ax.imshow(flatfield.T, cmap='inferno')
ax.set_xlabel('Spatial bin')
ax.set_ylabel('Spectral bin')
plt.show()