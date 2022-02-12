import matplotlib.pyplot as plt
import numpy as np
import pyuvs as pu

fig, ax = plt.subplots()

psf = pu.load_muv_point_spread_function()
detector_pixels = np.linspace(0, 180, num=181)
ax.plot(detector_pixels, psf)
ax.set_xlabel('Detector pixels')
ax.set_ylabel('Point spread function')
plt.show()