import matplotlib.pyplot as plt
import pyuvs as pu

fig, ax = plt.subplots()

template = pu.anc.load_template_no_nightglow()
wavelengths = pu.anc.load_muv_wavelength_centers()
ax.plot(wavelengths, template)
ax.set_xlim(wavelengths[0], wavelengths[-1])
ax.set_xlabel('Wavelength [nm]')
ax.set_ylabel('Relative brightness')

plt.show()