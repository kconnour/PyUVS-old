"""
Sensitivity Curves
==================

Plot the FUV and MUV sensitivity curves.

"""

# %%
# Import everything we'll need.

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pyuvs as pu

# %%
# Set the matplotlib rc params.

plt.rc('mathtext', fontset='stix')
plt.rc('font', **{'family': 'STIXGeneral'})
plt.rc('font', size=8)
plt.rc('axes', titlesize=8)
plt.rc('axes', labelsize=8)
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
plt.rc('legend', fontsize=8)
plt.rc('figure', titlesize=8)
plt.rc('pdf', fonttype=42)
plt.rc('ps', fonttype=42)
plt.rc('lines', linewidth=0.5)
plt.rc('axes', linewidth=0.5)
plt.rc('xtick.major', width=0.5)
plt.rc('xtick.minor', width=0.5)
plt.rc('ytick.major', width=0.5)
plt.rc('ytick.minor', width=0.5)
dpi = 150
plt.rc('savefig', dpi=dpi)

# %%
# Load the curves and plot them.

fig, axis = plt.subplots(1, 1, figsize=(3*1.618, 3), constrained_layout=True)

muv_factory = pu.load_muv_sensitivity_curve_manufacturer()
muv_obs = pu.load_muv_sensitivity_curve_observational()
fuv_factory = pu.load_fuv_sensitivity_curve_manufacturer()

axis.plot(fuv_factory[:, 0], fuv_factory[:, 1], color='#7F7F7F', linewidth=1)
axis.plot(muv_factory[:, 0], muv_factory[:, 1], color='#7F7F7F', linewidth=1)
axis.plot(muv_obs[:, 0], muv_obs[:, 1], color='#D62728', linewidth=1)

axis.text(140, 0.075, 'FUV', color='#7F7F7F')
axis.text(200, 0.01, 'MUV (June 9, 2014)', color='#7F7F7F')
axis.text(260, 0.05, 'MUV (October 19, 2018)', color='#D62728')

axis.xaxis.set_major_locator(ticker.MultipleLocator(30))
axis.xaxis.set_minor_locator(ticker.MultipleLocator(5))
axis.set_xlabel('Wavelength [nm]')
axis.yaxis.set_major_locator(ticker.MultipleLocator(0.02))
axis.yaxis.set_minor_locator(ticker.MultipleLocator(0.005))
axis.set_ylim(0, 0.1)
axis.set_ylabel('Detector Sensitivity [$\mathrm{DN}/(\mathrm{photons}/'
                '\mathrm{cm^2})$ at $\mathrm{gain} = 1$]')

plt.show()
