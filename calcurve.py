from pyuvs import *
import matplotlib.pyplot as plt
import numpy as np


manuf = load_muv_sensitivity_curve_manufacturer()
obs = load_muv_sensitivity_curve_observational()

newman = np.interp(obs[:, 0], manuf[:, 0], manuf[:, 1])

plt.plot(obs[:, 0], obs[:, 1] / newman)
plt.xlim(205, 306)
plt.ylim(0.8, 1.2)
plt.savefig('/home/kyle/ql_testing/div.png')