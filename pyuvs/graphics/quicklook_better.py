"""

"""
import spiceypy.utils.exceptions
from astropy.io import fits
import copy
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.ticker as ticker
from scipy.ndimage import gaussian_filter
from skimage.transform import resize
import spiceypy as spice
from pyuvs.files import FileFinder, DataFilenameCollection, orbit_code
from pyuvs.l1b.data_contents import L1bDataContents
from pyuvs.l1b.data_classifier import DataClassifier
from pyuvs.graphics.coloring import HistogramEqualizer
from pyuvs.spice import Spice
from pyuvs.constants import slit_width


class Colormaps:
    """ Make an object to hold predefined colormaps.

    """
    def __init__(self) -> None:
        self.__cmap = None
        self.__norm = None

    def set_magnetic_field(self) -> None:
        self.__cmap = plt.get_cmap('Blues_r')
        self.__norm = colors.Normalize(vmin=0, vmax=1)

    def set_local_time(self) -> None:
        self.__cmap = plt.get_cmap('twilight_shifted')
        self.__norm = colors.Normalize(vmin=6, vmax=18)

    def set_solar_zenith_angle(self) -> None:
        self.__cmap = plt.get_cmap('cividis_r')
        self.__norm = colors.Normalize(vmin=0, vmax=180)

    # TODO: surely this can be cleaner...
    def set_emission_angle(self) -> None:
        self.__cmap = colors.LinearSegmentedColormap.from_list(
            'cividis_half', copy.copy(plt.get_cmap('cividis_r'))
            (np.linspace(0, 0.5, 256)))
        self.__norm = colors.Normalize(vmin=0, vmax=90)

    def set_phase_angle(self) -> None:
        self.__cmap = plt.get_cmap('cividis_r')
        self.__norm = colors.Normalize(vmin=0, vmax=180)

    @property
    def cmap(self):
        return self.__cmap

    @property
    def norm(self):
        return self.__norm


class Colorbar:
    """Fill a colorbar. Add methods to add more info to it

    """
    def __init__(self, axis, cmap, norm):
        self.__axis = axis
        self.__cmap = cmap
        self.__norm = norm
        self.__colorbar = self.__make_colorbar()

    def __make_colorbar(self):
        data_sm = plt.cm.ScalarMappable(cmap=self.__cmap, norm=self.__norm)
        data_sm.set_array(np.array([]))
        return plt.colorbar(data_sm, cax=self.__axis)

    def set_label(self, label: str) -> None:
        self.__colorbar.set_label(label)

    def add_major_ticks(self, major_ticks: float) -> None:
        self.__colorbar.ax.yaxis.set_major_locator(
            ticker.MultipleLocator(major_ticks))

    def add_minor_ticks(self, minor_ticks: float) -> None:
        self.__colorbar.ax.yaxis.set_minor_locator(
            ticker.MultipleLocator(minor_ticks))


class QuicklookColorbarBundle:
    """Bundle together QL and its colorbar. Add methods to fill them.

    """
    def __init__(self, quicklook_ax: plt.Axes, colorbar_ax: plt.Axes) -> None:
        self.__quicklook_ax = quicklook_ax
        self.__colorbar_ax = colorbar_ax

    def fill_magnetic_field(self, files: DataFilenameCollection,
                            swath_number: list[int], flip: bool, spice_directory) -> None:
        cmap = Colormaps()
        cmap.set_magnetic_field()

        #ql = Quicklook(files, self.__quicklook_ax, swath_number, flip)
        #ql.fill_magnetic_field(spice_directory, cmap, norm)

        cbar = Colorbar(self.__colorbar_ax, cmap.cmap, cmap.norm)
        cbar.set_label('Closed field line probability')
        cbar.add_major_ticks(0.2)
        cbar.add_minor_ticks(0.05)

    def fill_local_time(self, files: DataFilenameCollection,
                        swath_number: list[int], flip: bool) -> None:
        cmap = Colormaps()
        cmap.set_local_time()

        #ql = Quicklook(files, self.__quicklook_ax, swath_number, flip)
        #ql.fill_local_time(cmap, norm)

        cbar = Colorbar(self.__colorbar_ax, cmap.cmap, cmap.norm)
        cbar.set_label('Local Time [hours]')
        cbar.add_major_ticks(3)
        cbar.add_minor_ticks(1)

    def fill_solar_zenith_angle(self, files: DataFilenameCollection,
                                swath_number: list[int], flip: bool) -> None:
        cmap = Colormaps()
        cmap.set_solar_zenith_angle()

        #ql = Quicklook(files, self.__quicklook_ax, swath_number, flip)
        #ql.fill_local_time(cmap, norm)

        cbar = Colorbar(self.__colorbar_ax, cmap.cmap, cmap.norm)
        cbar.set_label(r'Solar Zenith Angle [$\degree$]')
        cbar.add_major_ticks(30)
        cbar.add_minor_ticks(10)

    def fill_emission_angle(self, files: DataFilenameCollection,
                            swath_number: list[int], flip: bool) -> None:
        cmap = Colormaps()
        cmap.set_emission_angle()

        #ql = Quicklook(files, self.__quicklook_ax, swath_number, flip)
        #ql.fill_local_time(cmap, norm)

        cbar = Colorbar(self.__colorbar_ax, cmap.cmap, cmap.norm)
        cbar.set_label(r'Emission Angle [$\degree$]')
        cbar.add_major_ticks(15)
        cbar.add_minor_ticks(5)

    def fill_phase_angle(self, files: DataFilenameCollection,
                         swath_number: list[int], flip: bool) -> None:
        cmap = Colormaps()
        cmap.set_phase_angle()

        #ql = Quicklook(files, self.__quicklook_ax, swath_number, flip)
        #ql.fill_local_time(cmap, norm)

        cbar = Colorbar(self.__colorbar_ax, cmap.cmap, cmap.norm)
        cbar.set_label(r'Phase Angle [$\degree$]')
        cbar.add_major_ticks(30)
        cbar.add_minor_ticks(10)


class HighResolutionGeometryCreator:
    def __init__(self, spice_directory, context_map: np.ndarray,
                 artificial_positions: int, flip: bool):
        Spice().load_spice(spice_directory)
        self.__map = context_map
        self.__positions = artificial_positions
        self.__flip = flip

    def swath_geometry(self, file: L1bDataContents):
        return _SwathGeometryCreator(
            file, self.__map, self.__positions, self.__flip).arrays


class _SwathGeometryCreator:
    def __init__(self, file: L1bDataContents, context_map: np.ndarray,
                 artificial_positions: int, flip: bool):
        self.__file = file
        self.__map = context_map
        self.__positions = artificial_positions
        self.__integrations = self.__get_artificial_integrations()
        self.__arrays = _SwathArrays(self.__integrations, self.__positions)
        self.__flip = flip

        self.__target = 'Mars'
        self.__frame = 'IAU_Mars'
        self.__abcorr = 'LT+S'
        self.__observer = 'MAVEN'
        self.__body = 499
        self.__method = 'Ellipsoid'

        self.__et = self.__expand_et_to_new_pixel_centers()
        self.__pixel_vec = self.__expand_pixel_vec_to_new_pixel_centers()

        self.__fill_high_resolution_arrays()

    def __get_artificial_integrations(self):
        return int(self.__positions / self.__file.n_positions *
                   self.__file.n_integrations)

    def __expand_et_to_new_pixel_centers(self) -> np.ndarray:
        et = self.__file['integration'].data['et']
        native_et_diff = np.diff(et)
        native_et_edges = np.linspace(et[0] - native_et_diff[0] / 2,
                                      et[-1] + native_et_diff[-1] / 2,
                                      num=et.shape[0]+1)
        rescaled_et_edges = np.interp(
            np.linspace(0, self.__integrations, num=self.__integrations+1),
            np.linspace(0, self.__integrations, num=et.shape[0]+1),
            native_et_edges
        )
        rescaled_et_centers = (rescaled_et_edges[:-1] + rescaled_et_edges[1:]) / 2
        return np.broadcast_to(rescaled_et_centers,
                               (self.__positions, self.__integrations)).T

    def __expand_pixel_vec_to_new_pixel_centers(self) -> np.ndarray:
        pixel_vector = self.__file['pixelgeometry'].data['pixel_vec']
        rescaled_pixel_vec_edges = np.zeros((self.__integrations + 1,
                                             self.__positions + 1, 3))
        if self.__flip:
            lower_left = pixel_vector[0, :, 0, 0]
            upper_left = pixel_vector[-1, :, 0, 1]
            lower_right = pixel_vector[0, :, -1, 2]
            upper_right = pixel_vector[-1, :, -1, 3]
        else:
            lower_left = pixel_vector[0, :, 0, 1]
            upper_left = pixel_vector[-1, :, 0, 0]
            lower_right = pixel_vector[0, :, -1, 3]
            upper_right = pixel_vector[-1, :, -1, 2]
        for e in range(3):
            a = np.linspace(lower_left[e], upper_left[e],
                            num=self.__integrations + 1)
            b = np.linspace(lower_right[e], upper_right[e],
                            num=self.__integrations + 1)
            rescaled_pixel_vec_edges[:, :, e] = np.array(
                [np.linspace(i, j, self.__positions + 1) for i, j in zip(a, b)])

        return (rescaled_pixel_vec_edges[:-1, :-1, :] +
                rescaled_pixel_vec_edges[1:, 1:, :])/2

    def __compute_pixel_surface_intercept(self, et, pixel_vector):
        return spice.sincpt(
            self.__method, self.__target, et, self.__frame, self.__abcorr,
            self.__observer, self.__frame, pixel_vector)

    def __compute_illumination_angles(self, et, spoint):
        return spice.ilumin(
            self.__method, self.__target, et, self.__frame, self.__abcorr,
            self.__observer, spoint)

    def __get_pixel_values(self, et, pixel_vector):
        try:
            spoint, trgepc, srfvec = \
                self.__compute_pixel_surface_intercept(et, pixel_vector)
            trgepc, srfvec, phase, solar, emission = \
                self.__compute_illumination_angles(et, spoint)
        except spiceypy.utils.exceptions.NotFoundError:
            return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan

        rpoint, colatpoint, lonpoint = spice.recsph(spoint)

        if lonpoint < 0:
            lonpoint += 2 * np.pi

        hr, mn, sc, time, ampm = spice.et2lst(
            et, self.__body, lonpoint, 'planetocentric', timlen=256,
            ampmlen=256)

        latitude = np.degrees(np.pi / 2 - colatpoint)
        longitude = np.degrees(lonpoint)
        local_time = hr + mn / 60 + sc / 3600
        solar_zenith_angle = np.degrees(solar)
        emission_angle = np.degrees(emission)
        phase_angle = np.degrees(phase)
        map_lat = int(np.round(np.degrees(colatpoint), 1) * 10)
        map_lon = int(np.round(np.degrees(lonpoint), 1) * 10)
        context_map = self.__map[map_lat, map_lon]
        return latitude, longitude, local_time, solar_zenith_angle, \
               emission_angle, phase_angle, context_map

    def __fill_high_resolution_arrays(self):
        latitude = self.__arrays.latitude
        longitude = self.__arrays.longitude
        local_time = self.__arrays.local_time
        solar_zenith_angle = self.__arrays.solar_zenith_angle
        emission_angle = self.__arrays.emission_angle
        phase_angle = self.__arrays.phase_angle
        context_map = self.__arrays.context_map
        for i in range(latitude.shape[0]):
            for j in range(latitude.shape[1]):
                et = self.__et[i, j]
                pixel_vector = self.__pixel_vec[i, j, :]
                lat, lon, lt, sza, ea, pa, con_map = \
                    self.__get_pixel_values(et, pixel_vector)
                latitude[i, j] = lat
                longitude[i, j] = lon
                local_time[i, j] = sza
                solar_zenith_angle[i, j] = sza
                emission_angle[i, j] = ea
                phase_angle[i, j] = pa
                context_map[i, j] = con_map

        self.__arrays.latitude = latitude
        self.__arrays.longitude = longitude
        self.__arrays.local_time = local_time
        self.__arrays.solar_zenith_angle = solar_zenith_angle
        self.__arrays.emission_angle = emission_angle
        self.__arrays.phase_angle = phase_angle
        self.__arrays.context_map = context_map

    @property
    def arrays(self):
        return self.__arrays


class _SwathArrays:
    def __init__(self, integrations, positions):
        shape = (integrations, positions)
        self.__latitude = self.__make_array_of_nans(shape)
        self.__longitude = self.__make_array_of_nans(shape)
        self.__local_time = self.__make_array_of_nans(shape)
        self.__solar_zenith_angle = self.__make_array_of_nans(shape)
        self.__emission_angle = self.__make_array_of_nans(shape)
        self.__phase_angle = self.__make_array_of_nans(shape)
        self.__context_map = self.__make_array_of_nans(shape + (4,))

    @staticmethod
    def __make_array_of_nans(shape: tuple) -> np.ndarray:
        return np.zeros(shape) * np.nan

    @property
    def latitude(self):
        return self.__latitude

    @latitude.setter
    def latitude(self, val):
        self.__latitude = val

    @property
    def longitude(self):
        return self.__longitude

    @longitude.setter
    def longitude(self, val):
        self.__longitude = val

    @property
    def local_time(self):
        return self.__local_time

    @local_time.setter
    def local_time(self, val):
        self.__local_time = val

    @property
    def solar_zenith_angle(self):
        return self.__solar_zenith_angle

    @solar_zenith_angle.setter
    def solar_zenith_angle(self, val):
        self.__solar_zenith_angle = val

    @property
    def emission_angle(self):
        return self.__emission_angle

    @emission_angle.setter
    def emission_angle(self, val):
        self.__emission_angle = val

    @property
    def phase_angle(self):
        return self.__phase_angle

    @phase_angle.setter
    def phase_angle(self, val):
        self.__phase_angle = val

    @property
    def context_map(self):
        return self.__context_map

    @context_map.setter
    def context_map(self, val):
        self.__context_map = val


class Quicklook:
    def __init__(self, files: DataFilenameCollection, ax: plt.Axes,
                 swath_numbers: list[int], flip: bool) -> None:
        """
        Parameters
        ----------
        files
            A collection of files to plot a quicklook for.
        ax
            The axis to put the quicklook into.
        swath_numbers
            The swath numbers for each of the swaths in the files.
        flip
            Denote whether the files were beta-angle flipped.

        """
        self.__files = files
        self.__ax = ax
        self.__swath_numbers = swath_numbers
        self.__flip = flip
        self.__slit_width = 10.64

if __name__ == '__main__':
    from pyuvs.files import FileFinder
    files = FileFinder('/media/kyle/Samsung_T5/IUVS_data').soschob(3453, segment='apoapse', channel='muv')
    hrgc = HighResolutionGeometryCreator('/media/kyle/Samsung_T5/IUVS_data/spice',
                                         np.load('/home/kyle/repos/pyuvs/aux/mars_surface_map.npy'), 200, False)

    for f in files.filenames:
        l1b = L1bDataContents(f)
        arrays = hrgc.swath_geometry(l1b)
        print(arrays.latitude.shape)
        raise SystemExit(9)
