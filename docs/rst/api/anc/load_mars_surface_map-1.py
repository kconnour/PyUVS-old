import matplotlib.pyplot as plt
import pyuvs as pu

surface_map = pu.anc.load_mars_surface_map()
plt.imshow(surface_map)
plt.show()