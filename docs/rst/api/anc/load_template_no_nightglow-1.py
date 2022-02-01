import matplotlib.pyplot as plt
import numpy as np
import pyuvs as pu

fig, ax = plt.subplots()

templates = pu.anc.load_template_no_nightglow()
wavelengths = pu.anc.load_muv_wavelength_center()
ax.plot(wavelengths, np.sum(wavelengths, axis=0))
ax.set_xlim(wavelengths[0], wavelengths[-1])
ax.set_xlabel('Wavelength [nm]')
ax.set_ylabel('Relative brightness')
plt.show()