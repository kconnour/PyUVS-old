"""MLR = multiple linear regression
"""
from pathlib import Path
import statsmodels.api as sm
from pyuvs.anc import load_template_no_nightglow, load_muv_wavelength_center, load_muv_sensitivity_curve_observational
from pyuvs.data_files import find_latest_apoapse_muv_file_paths_from_block, L1bFile
import numpy as np
import matplotlib.pyplot as plt
from pyuvs.constants import pixel_omega, kR


if __name__ == '__main__':
    p = Path('/media/kyle/Samsung_T5/IUVS_data')
    files = find_latest_apoapse_muv_file_paths_from_block(p, 4000)
    file = L1bFile(files[2])

    no_templates = load_template_no_nightglow(detector=True)[1:, :]
    wavelength_center = load_muv_wavelength_center()
    '''
    # Here we just made a clean NO template that I no longer have to make every time
    gross_template = np.genfromtxt('/home/kyle/Downloads/no_nightglow_detector_1024-bins.dat')

    no_templates = sm.add_constant(no_templates.T)
    results = sm.OLS(gross_template, no_templates).fit()
    foo = ['constant', 'gammav0', 'gammav3', 'delta', 'epsilon']
    print(results.summary(xname=foo))
    #plt.plot(wavelength_center, gross_template, color='gray')
    #plt.plot(wavelength_center, results.predict(no_templates), color='r', linewidth=0.5, linestyle='--')
    #plt.savefig('/home/kyle/junk.png')

    pred_template = results.predict(no_templates)
    np.save('/home/kyle/repos/PyUVS/pyuvs/anc/templates/no_nightglow_template_detector_from_zac_the_ultimate.npy', pred_template)'''

    # Load in the templates
    no_template = np.load('/home/kyle/repos/PyUVS/pyuvs/anc/templates/no_nightglow_template_detector_from_zac_the_ultimate.npy')
    solar_template = np.genfromtxt('/home/kyle/Downloads/zacs_data_files/solar_continuum_detector_1024-bins.dat')
    co_cameron_template = np.genfromtxt('/home/kyle/Downloads/zacs_data_files/co-cameron-bands_detector_1024-bins.dat')
    uvd_template = np.genfromtxt('/home/kyle/Downloads/zacs_data_files/co2p_uvd_detector_1024-bins.dat')

    # Rebin the templates to match the data binning
    spectral_pixel_bin_width = int(np.median(file.binning.spectral_pixel_bin_width))
    def rebin_template(template, spe_pix_bin_width):
        return template.reshape((int(template.shape[0]/spe_pix_bin_width), spe_pix_bin_width)).sum(axis=1)
    rebin_no_template = rebin_template(no_template, spectral_pixel_bin_width)
    rebin_solar_template = rebin_template(solar_template, spectral_pixel_bin_width)
    rebin_co_cameron_template = rebin_template(co_cameron_template, spectral_pixel_bin_width)
    rebin_uvd_template = rebin_template(uvd_template, spectral_pixel_bin_width)
    rebin_aurora_template = rebin_co_cameron_template + rebin_uvd_template

    # Stack all templates together
    templates = np.vstack([rebin_no_template, rebin_aurora_template, rebin_solar_template]).T   # (n_wavelengths, 3)
    templates = sm.add_constant(templates)
    dummy_spectrum = file.detector_dark_subtracted[-1, 25, :]
    dummy_unc = file.random_uncertainty_dn[-1, 25, :]

    observation = np.full_like(templates[:, 0], fill_value=np.nan)
    starting_spectral_index = int(file.binning.spectral_pixel_bin_width[0] / spectral_pixel_bin_width)
    observation[starting_spectral_index:starting_spectral_index+dummy_spectrum.shape[0]] = dummy_spectrum
    unc = np.full_like(templates[:, 0], fill_value=np.nan)
    unc[starting_spectral_index:starting_spectral_index + dummy_spectrum.shape[0]] = dummy_unc
    def rebin_wavelengths(wavs, spe_pix_bin_width):
        return wavs.reshape((int(wavs.shape[0]/spe_pix_bin_width), spe_pix_bin_width)).mean(axis=1)
    rebinned_wavelengths = rebin_wavelengths(wavelength_center, spectral_pixel_bin_width)

    '''We have now taken our 40 bin spectrum and placed it in its original 
    position within a 256 bin spectrum so we can fit it to the 256 bin template
    '''

    fit = sm.WLS(observation, templates, weights=1/unc**2, missing='drop').fit()   # This ignores NaNs
    coeff = fit.params
    new_sensitivity_curve = np.interp(rebinned_wavelengths, load_muv_sensitivity_curve_observational()[:, 0],
                                      load_muv_sensitivity_curve_observational()[:, 1])
    spatial_bin_width = int(np.median(file.binning.spatial_pixel_bin_width))
    w_width = np.median(file.observation.wavelength_width)
    gn = file.observation.mcp_gain
    int_time = file.observation.integration_time
    def calculate_calibration_curve(spa_bin_wid, new_calib_curve, wav_width, gain, itime):
        """DN/kR"""
        bin_omega = pixel_omega * spa_bin_wid
        return wav_width * gain * itime * kR * new_calib_curve * bin_omega

    calcurve = calculate_calibration_curve(spatial_bin_width, new_sensitivity_curve, w_width, gn, int_time)
    no_brightness = np.sum(coeff[1] * templates[:, 1] * w_width / calcurve)
    print(no_brightness)

    # Zac's ass-ertion: interp the sensitivity curve to 1024 binning
