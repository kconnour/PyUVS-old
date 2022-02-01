import glob

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import statsmodels.api as sm
from pyuvs.l1b.data_contents import L1bDataContents
from pyuvs.constants import cmos_pixel_well_depth, pixel_omega, kR
from pyuvs.anc.templates import NitricOxideNightglow
from pyuvs.anc.sensitivity import FUVCurve, FUVWavelengths, MUVCurve, \
    MUVWavelengths
from pyuvs.files import DataFilename

from astropy.io import fits

orbit_number = 5738
files = sorted(glob.glob(
    f'/Volumes/MAVEN Data/iuvs_data/level1b/orbit05700/*l1b_apoapse-orbit{orbit_number:0>5}-muv*.fits.gz'))


class _InstrumentSettings:

    def __init__(self, contents: L1bDataContents):
        self.__contents = contents
        self.__settings = self.__get_settings()

    def __get_settings(self) -> dict:
        return {
            'channel': self.__contents['primary'].header['xuv'].lower(),
            #'detector_voltage': self.__contents['primary'].header['mcp_volt'],
            'detector_gain': self.__contents['observation'].data['mcp_gain'][0],
            'integration_time': self.__contents['primary'].header['int_time'],
            'spectral_bin_width': self.__contents['primary'].header['spe_size'],
            'spectral_pixel_start': self.__contents['primary'].header[
                'spe_ofs'],
            'spatial_bin_width': self.__contents['primary'].header['spa_size'],
            'spatial_pixel_start': self.__contents['primary'].header['spa_ofs'],
            'wavelengths': self.__contents['observation'].data['wavelength'][0],
            'wavelength_width': np.median(
                self.__contents['observation'].data['wavelength_width'][0])
        }

    @property
    def settings(self):
        return self.__settings


class CalibrationCurve:

    def __init__(self, instrument_settings: dict, sensitivity: _AuxiliaryDict):
        self.__instrument_settings = instrument_settings
        self.__wavelength = sensitivity['wavelength']
        self.__sensitivity = sensitivity['sensitivity']
        self.__detector_calibration = self.__calculate_calibration_curve()

    def __calculate_calibration_curve(self):
        """DN/kR"""

        bin_omega = pixel_omega * self.__instrument_settings[
            'spatial_bin_width']
        line_effective_area = np.array(
            [np.interp(i, self.__wavelength, self.__sensitivity) for i in
             self.__instrument_settings['wavelengths']])
        return self.__instrument_settings['wavelength_width'] * \
               self.__instrument_settings['detector_gain'] * \
               self.__instrument_settings[
                   'integration_time'] * kR * line_effective_area * bin_omega

    @property
    def detector_calibration(self):
        return self.__detector_calibration


class MLRFitter:

    def __init__(self, spectrum, spectrum_uncertainty, templates,
                 template_names):
        self.__spectrum = spectrum
        self.__spectrum_uncertainty = spectrum_uncertainty
        self.__templates = self.__add_constant_to_templates(templates)
        self.__template_names = self.__add_constant_to_template_names(
            template_names)
        self.__fit = self.__fit_templates()

    @staticmethod
    def __add_constant_to_templates(templates):
        return sm.add_constant(templates.T).T

    @staticmethod
    def __add_constant_to_template_names(template_names):
        template_names = list(template_names)
        template_names.insert(0, 'constant')
        return np.array(template_names)

    def __fit_templates(self):
        weights = 1 / (self.__spectrum_uncertainty ** 2)
        model = sm.WLS(self.__spectrum, self.__templates.T, weights=weights, missing='drop')   # if saturated pixels are NaNs, this ignores them
        return model.fit()

    def save_fit_summary(self, filepath):
        summary = self.__fit.summary(xname=list(self.__template_names))
        with open(filepath, 'a') as summary_file:
            summary_file.write(summary.as_text())

    @property
    def fit_coefficients(self):
        return self.__fit.params

    @property
    def fit_uncertainties(self):
        return self.__fit.bse

    @property
    def fit_residuals(self):
        return self.__fit.resid

    @property
    def fit_rsquared(self):
        return self.__fit.rsquared

    @property
    def template_names(self):
        return self.__template_names

    def get_integrated_intensity(self, calibration_curve, wavelength_width):
        return np.array([np.sum(self.fit_coefficients[i] * self.__templates[
            i] / calibration_curve * wavelength_width)
                         for i in range(1, len(self.__templates))])

    def get_integrated_intensity_uncertainty(self, calibration_curve,
                                             wavelength_width):
        return np.array([np.sum(self.fit_uncertainties[i] * self.__templates[
            i] / calibration_curve * wavelength_width)
                         for i in range(1, len(self.__templates))])

    def get_integrated_intensity_and_uncertainty(self, calibration_curve,
                                                 wavelength_width):
        return self.get_integrated_intensity(calibration_curve,
                                             wavelength_width), self.get_integrated_intensity_uncertainty(
            calibration_curve, wavelength_width)

    def get_fit_constant(self):
        return self.__fit.params[0]


class PipelineMLR:

    def __init__(self, contents: L1bDataContents):
        self.__l1b = contents
        self.__instrument_settings = _InstrumentSettings(contents).settings
        self.__raise_value_error_if_invalid_binning_table()
        self.__saturation_threshold = self.__calculate_saturation_threshold()
        self.__sensitivity_curve = self.__load_sensitivity_curve()
        self.__detector_calibration = self.__calculate_calibration_curve()
        fit_array, radiance_array, uncertainty_array, features = self.__perform_pixel_by_pixel_mlr_fit()
        self.__fits = fit_array
        self.__radiances = radiance_array
        self.__uncertainties = uncertainty_array
        self.__features = features

    def __raise_value_error_if_invalid_binning_table(self):
        if self.__instrument_settings['spectral_pixel_start'] % \
                self.__instrument_settings['spectral_bin_width'] != 0:
            raise ValueError(
                'Invalid binning table. Contact Justin Deighan for assistance: justin.deighan@lasp.colorado.edu.')

    def __calculate_saturation_threshold(self):
        return cmos_pixel_well_depth * self.__instrument_settings[
            'spatial_bin_width'] * self.__instrument_settings[
                   'spectral_bin_width']

    def __load_sensitivity_curve(self):
        return MUVSensitivityPipeline() if self.__instrument_settings[
                                               'channel'] == 'muv' else FUVSensitivity()

    def __calculate_calibration_curve(self):
        return CalibrationCurve(self.__instrument_settings,
                                self.__sensitivity_curve).detector_calibration

    def __load_nightside_templates(self):

        # TODO: implement FUV fitting
        templates = NightsideMUVTemplates()

        n_spectral_bins = int(
            1024 / self.__instrument_settings['spectral_bin_width'])
        pixel_start = int(self.__instrument_settings['spectral_pixel_start'] /
                          self.__instrument_settings['spectral_bin_width'])
        if n_spectral_bins != 1024:
            return list(templates.keys()), np.array(
                [self.__rebin_factor(templates[i]) for i in
                 list(templates.keys())])[:,
                                           pixel_start:pixel_start + l1b.n_wavelengths]
        else:
            return list(templates.keys()), np.array(
                [templates[i] for i in list(templates.keys())])[:,
                                           pixel_start:pixel_start + l1b.n_wavelengths]

    # Take 1024 template and rebin it to whatever binning scheme
    def __rebin_factor(self, array: np.ndarray):
        new_spectrum = np.array([np.sum(
            array[i:i + self.__instrument_settings['spectral_bin_width']]) for i
                                 in range(0, len(array) -
                                          self.__instrument_settings[
                                              'spectral_bin_width'],
                                          self.__instrument_settings[
                                              'spectral_bin_width'])])
        new_spectrum /= np.sum(
            new_spectrum * self.__instrument_settings['wavelength_width'])
        return new_spectrum

    def __perform_pixel_by_pixel_mlr_fit(self):
        template_names, templates = self.__load_nightside_templates()
        fit_array = np.zeros(
            (self.__l1b.n_integrations, self.__l1b.n_positions), dtype=object)
        radiance_array = np.zeros((self.__l1b.n_integrations,
                                   self.__l1b.n_positions, len(template_names)))
        uncertainty_array = np.zeros((self.__l1b.n_integrations,
                                      self.__l1b.n_positions,
                                      len(template_names)))
        for integration in range(self.__l1b.n_integrations):
            for spatial_bin in range(self.__l1b.n_positions):
                spectrum = self.__l1b['detector_dark_subtracted'].data[
                    integration, spatial_bin]
                spectrum_uncertainty = self.__l1b['random_dn_unc'].data[
                    integration, spatial_bin]
                fit = MLRFitter(spectrum, spectrum_uncertainty, templates,
                                template_names)
                fit_array[integration, spatial_bin] = fit
                radiance_array[
                    integration, spatial_bin] = fit.get_integrated_intensity(
                    self.__detector_calibration[spatial_bin],
                    self.__instrument_settings['spectral_bin_width'])
                uncertainty_array[
                    integration, spatial_bin] = fit.get_integrated_intensity_uncertainty(
                    self.__detector_calibration[spatial_bin],
                    self.__instrument_settings['spectral_bin_width'])
        return fit_array, radiance_array, uncertainty_array, np.array(
            template_names)

    @property
    def no_nightglow_radiance(self):
        ind = np.squeeze(np.where(self.__features == 'no_nightglow'))
        return self.__radiances[:, :, ind]

    @property
    def no_nightglow_uncertainty(self):
        ind = np.squeeze(np.where(self.__features == 'no_nightglow'))
        return self.__uncertainties[:, :, ind]

    @property
    def aurora_radiance(self):
        ind = np.squeeze(np.where((self.__features == 'co_cameron_bands') |
                                  (self.__features == 'co2p_uvd') |
                                  (self.__features == 'o2972') |
                                  (self.__features == 'co2p_fdb')))
        return np.sum(self.__radiances[:, :, ind], axis=2)

    @property
    def aurora_uncertainty(self):
        ind = np.squeeze(np.where((self.__features == 'co_cameron_bands') |
                                  (self.__features == 'co2p_uvd') |
                                  (self.__features == 'o2972') |
                                  (self.__features == 'co2p_fdb')))
        return np.sum(self.__uncertainties[:, :, ind], axis=2)


if __name__ == '__main__':
    df = DataFilename(files[7])
    l1b = L1bDataContents(df)
    img = PipelineMLR(l1b).aurora_radiance
    img = plt.imshow(img, norm=colors.PowerNorm(gamma=1 / 2, vmin=0, vmax=10))
    plt.colorbar()
    plt.show()


