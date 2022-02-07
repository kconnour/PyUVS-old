import matplotlib.pyplot as plt
import pyuvs as pu

fig, ax = plt.subplots()

surface_map = pu.anc.load_map_mars_surface()
ax.imshow(surface_map)
plt.show()