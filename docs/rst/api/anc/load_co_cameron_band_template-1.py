import matplotlib.pyplot as plt
import pyuvs as pu

fig, ax = plt.subplots()

template = pu.anc.load_co_cameron_band_template()
wavelengths = pu.anc.load_muv_wavelength_center()
ax.plot(wavelengths, template)
ax.set_xlim(wavelengths[0], wavelengths[-1])
ax.set_xlabel('Wavelength [nm]')
ax.set_ylabel('Relative brightness')
plt.show()