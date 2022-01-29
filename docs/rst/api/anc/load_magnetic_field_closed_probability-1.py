import matplotlib.pyplot as plt
import pyuvs as pu

b_field = pu.anc.load_magnetic_field_closed_probability()
plt.imshow(b_field, cmap='Blues_r', origin='lower')
plt.show()