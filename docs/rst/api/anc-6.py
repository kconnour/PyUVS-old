import matplotlib.pyplot as plt
import numpy as np
import pyuvs as pu

fig, ax = plt.subplots()

curve = pu.load_fuv_sensitivity_curve_manufacturer()
ax.plot(curve[:, 0], curve[:, 1])
ax.set_xlabel('Wavelength [nm]')
ax.set_ylabel('Detector Sensitivity')
ax.set_xlim(100, 200)
ax.set_ylim(0, 0.1)
plt.show()