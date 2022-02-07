import matplotlib.pyplot as plt
import pyuvs as pu

fig, ax = plt.subplots()

b_field = pu.anc.load_map_magnetic_field_closed_probability()
ax.imshow(b_field, cmap='Blues_r', origin='lower')
plt.show()