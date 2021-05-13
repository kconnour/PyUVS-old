"""
ApoapseMUVQuicklookCreator
ApoapseMUVQuicklook
Banner
Colorbar                             (done)
Quicklook
QuicklookColorbarBundle
AuxillaryArray                       (done)
SurfaceGeographyMap                  (done)
MagneticFieldMap                     (done)
Colormaps                            (done)
HighResolutionGeometryCreator
_SwathGeometryCreator
_SwathArrays

"""
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
import spiceypy.utils.exceptions
from pyuvs.files import FileFinder, DataFilenameCollection, orbit_code
from pyuvs.l1b.data_contents import L1bDataContents
from pyuvs.l1b.data_classifier import DataClassifier
from pyuvs.graphics.coloring import HistogramEqualizer
from pyuvs.spice import Spice
from pyuvs.constants import slit_width


# TODO: Add ability to choose spectral indices in HistogramEqualizer
# TODO: this breaks on a single integration
# TODO: should HEQ break if I try to apply the coloring to a file that didn't
#  make the coloring?
# TODO banner
# TODO: choose scaling factor instead of positions
class ApoapseMUVQuicklook:
    def __init__(self, files: DataFilenameCollection, flatfield: np.ndarray,
                 swath_numbers: list[int], flip: bool, spice_directory: str,
                 ) -> None:
        self.__files = files
        self.__flatfield = flatfield
        self.__swath_numbers = swath_numbers
        self.__n_swaths = self.__swath_numbers[-1] + 1
        self.__flip = flip
        self.__spice_directory = spice_directory

        self.__axes = self.__setup_fig_and_axes()
        self.__make_banner()

    def __setup_fig_and_axes(self):
        self.__set_quicklook_rc_params()
        fig, axis_grid = self.__make_axis_grid()
        self.__combine_top_axes_rows(fig, axis_grid)
        return self.__create_axis_dict(fig.axes)

    # TODO: I hate this function and I can't completely identify why
    @staticmethod
    def __set_quicklook_rc_params() -> None:
        # Make sure the typeface isn't outlined when saved as a .pdf
        plt.rc('pdf', fonttype=42)  # ???
        plt.rc('ps', fonttype=42)  # postscript

        # Set the plot to be $\LaTeXe{}$-like
        plt.rc('font', **{'family': 'STIXGeneral'})  # Set the typeface to stix
        plt.rc('mathtext', fontset='stix')  # Set all math font to stix
        plt.rc('text', usetex=False)

        plt_thick = 0.5
        plt.rc('lines', linewidth=plt_thick)
        plt.rc('axes', linewidth=plt_thick)

    @staticmethod
    def __make_axis_grid():
        text_axis_height = 1
        data_axis_height = 2
        angular_axis_height = 1
        colorbar_width = 1/15
        height_ratios = [text_axis_height, data_axis_height, data_axis_height,
                         angular_axis_height, angular_axis_height]
        width_ratios = [1, colorbar_width, 1, colorbar_width]

        fig, axes = plt.subplots(5, 4, figsize=(6, 8),
                                 gridspec_kw={'height_ratios': height_ratios,
                                              'width_ratios': width_ratios},
                                 constrained_layout=True)
        return fig, axes

    def __combine_top_axes_rows(self, fig, axes):
        self.__combine_row_of_axes(fig, axes, 0, None)
        self.__combine_row_of_axes(fig, axes, 1, 3)
        self.__combine_row_of_axes(fig, axes, 2, 3)

    @staticmethod
    def __combine_row_of_axes(fig, axes, row, end_index):
        gs = axes[row, 0].get_gridspec()
        [ax.remove() for ax in axes[row, :end_index]]
        fig.add_subplot(gs[row, :end_index])
        return fig, axes

    @staticmethod
    def __create_axis_dict(axes):
        return {'text': axes[10],
                'data': axes[11],
                'data_colorbar': axes[0],
                'geography': axes[12],
                'geography_colorbar': axes[1],
                'local_time': axes[2],
                'local_time_colorbar': axes[3],
                'solar_zenith_angle': axes[4],
                'solar_zenith_angle_colorbar': axes[5],
                'emission_angle': axes[6],
                'emission_angle_colorbar': axes[7],
                'phase_angle': axes[8],
                'phase_angle_colorbar': axes[9]}

    def __make_banner(self):
        ban = Banner(self.__axes['text'])

    def fill_plots_no_nightglow(self):
        map_dir = np.load('/home/kyle/repos/pyuvs/aux/mars_surface_map.npy')
        hrgc = HighResolutionGeometryCreator(
            self.__spice_directory, map_dir, 200, self.__flip)

        map_ql = self.__setup_map_quicklook()
        lt_bundle = self.__setup_local_time_bundle()
        sza_bundle = self.__setup_solar_zenith_angle_bundle()
        ea_bundle = self.__setup_emission_angle_bundle()
        pa_bundle = self.__setup_phase_angle_bundle()

        for c, f in enumerate(self.__files.filenames):
            arrays = hrgc.swath_geometry(L1bDataContents(f))

            map_ql.plot_precomputed_swath_map(
                arrays.context_map, arrays.x, arrays.y, arrays.cx,
                self.__swath_numbers[c])
            lt_bundle.plot_precomputed_swath_bundle_from_cmap(
                arrays.local_time, arrays.x, arrays.y,
                self.__swath_numbers[c])
            sza_bundle.plot_precomputed_swath_bundle_from_cmap(
                arrays.solar_zenith_angle, arrays.x, arrays.y,
                self.__swath_numbers[c])
            ea_bundle.plot_precomputed_swath_bundle_from_cmap(
                arrays.emission_angle, arrays.x, arrays.y,
                self.__swath_numbers[c])
            pa_bundle.plot_precomputed_swath_bundle_from_cmap(
                arrays.phase_angle, arrays.x, arrays.y,
                self.__swath_numbers[c])

    def fill_plots_aurora(self):
        map_dir = np.load('/home/kyle/repos/pyuvs/aux/magnetic_field_closed_probability.npy')
        hrgc = HighResolutionGeometryCreator(
            self.__spice_directory, map_dir, 200, self.__flip)

        map_ql = self.__setup_map_quicklook()
        lt_bundle = self.__setup_local_time_bundle()
        sza_bundle = self.__setup_solar_zenith_angle_bundle()
        ea_bundle = self.__setup_emission_angle_bundle()
        pa_bundle = self.__setup_phase_angle_bundle()

        for c, f in enumerate(self.__files.filenames):
            arrays = hrgc.swath_geometry(L1bDataContents(f))

            map_ql.plot_precomputed_swath_map(
                arrays.context_map, arrays.x, arrays.y, arrays.cx,
                self.__swath_numbers[c])
            lt_bundle.plot_precomputed_swath_bundle_from_cmap(
                arrays.local_time, arrays.x, arrays.y,
                self.__swath_numbers[c])
            sza_bundle.plot_precomputed_swath_bundle_from_cmap(
                arrays.solar_zenith_angle, arrays.x, arrays.y,
                self.__swath_numbers[c])
            ea_bundle.plot_precomputed_swath_bundle_from_cmap(
                arrays.emission_angle, arrays.x, arrays.y,
                self.__swath_numbers[c])
            pa_bundle.plot_precomputed_swath_bundle_from_cmap(
                arrays.phase_angle, arrays.x, arrays.y,
                self.__swath_numbers[c])

    def __setup_map_quicklook(self):
        map_ql = Quicklook(self.__axes['geography'])
        self.__axes['geography_colorbar'].remove()
        map_ql.turn_off_plot_ticks()
        map_ql.set_background_black()
        map_ql.set_axis_limits(self.__n_swaths)
        return map_ql

    def __setup_magnetic_field_bundle(self):
        colormap = Colormaps()
        colormap.set_magnetic_field()
        field_bundle = QuicklookColorbarBundle(
            self.__axes['geography'],
            self.__axes['geography_colorbar'],
            colormap.cmap, colormap.norm
        )
        field_bundle.turn_off_plot_ticks()
        field_bundle.set_background_black()
        field_bundle.set_axis_limits(self.__n_swaths)
        field_bundle.set_label('Closed field line probability')
        field_bundle.add_major_ticks(0.2)
        field_bundle.add_minor_ticks(0.05)
        return field_bundle

    def __setup_local_time_bundle(self):
        colormap = Colormaps()
        colormap.set_local_time()
        lt_bundle = QuicklookColorbarBundle(
            self.__axes['local_time'],
            self.__axes['local_time_colorbar'],
            colormap.cmap, colormap.norm)
        lt_bundle.turn_off_plot_ticks()
        lt_bundle.set_background_black()
        lt_bundle.set_axis_limits(self.__n_swaths)
        lt_bundle.set_label('Local Time [hours]')
        lt_bundle.add_major_ticks(3)
        lt_bundle.add_minor_ticks(1)
        return lt_bundle

    def __setup_solar_zenith_angle_bundle(self):
        colormap = Colormaps()
        colormap.set_solar_zenith_angle()
        sza_bundle = QuicklookColorbarBundle(
            self.__axes['solar_zenith_angle'],
            self.__axes['solar_zenith_angle_colorbar'],
            colormap.cmap, colormap.norm)
        sza_bundle.turn_off_plot_ticks()
        sza_bundle.set_background_black()
        sza_bundle.set_axis_limits(self.__n_swaths)
        sza_bundle.set_label(r'Solar Zenith Angle [$\degree$]')
        sza_bundle.add_major_ticks(30)
        sza_bundle.add_minor_ticks(10)
        return sza_bundle

    def __setup_emission_angle_bundle(self):
        colormap = Colormaps()
        colormap.set_emission_angle()
        ea_bundle = QuicklookColorbarBundle(
            self.__axes['emission_angle'],
            self.__axes['emission_angle_colorbar'],
            colormap.cmap, colormap.norm)
        ea_bundle.turn_off_plot_ticks()
        ea_bundle.set_background_black()
        ea_bundle.set_axis_limits(self.__n_swaths)
        ea_bundle.set_label(r'Emission Angle [$\degree$]')
        ea_bundle.add_major_ticks(15)
        ea_bundle.add_minor_ticks(5)
        return ea_bundle

    def __setup_phase_angle_bundle(self):
        colormap = Colormaps()
        colormap.set_phase_angle()
        pa_bundle = QuicklookColorbarBundle(
            self.__axes['phase_angle'],
            self.__axes['phase_angle_colorbar'],
            colormap.cmap, colormap.norm)
        pa_bundle.turn_off_plot_ticks()
        pa_bundle.set_background_black()
        pa_bundle.set_axis_limits(self.__n_swaths)
        pa_bundle.set_label(r'Phase Angle [$\degree$]')
        pa_bundle.add_major_ticks(30)
        pa_bundle.add_minor_ticks(10)
        return pa_bundle

    @staticmethod
    def savefig(location: str) -> None:
        plt.savefig(location, dpi=300)


class Banner:
    def __init__(self, axis):
        self.__axis = axis
        self.__setup_axis()

    def __setup_axis(self):
        self.__turn_off_text_frame()
        self.__turn_off_plot_ticks()

    def __turn_off_text_frame(self) -> None:
        self.__axis.set_frame_on(False)

    def __turn_off_plot_ticks(self) -> None:
        self.__axis.set_xticks([])
        self.__axis.set_yticks([])


class Quicklook:
    def __init__(self, axis):
        self.__axis = axis

    def set_axis_limits(self, n_swaths: int) -> None:
        self.__axis.set_xlim(0, slit_width * n_swaths)
        self.__axis.set_ylim(60, 120)

    def set_background_black(self) -> None:
        self.__axis.set_facecolor((0, 0, 0))

    def turn_off_plot_ticks(self) -> None:
        self.__axis.set_xticks([])
        self.__axis.set_yticks([])

    def plot_precomputed_swath_map(self, array, x, y, cx, swath_number) -> None:
        y = (120 - y) + 60
        # offset X array by swath number
        X = x + slit_width * swath_number

        array = array.reshape(array.shape[0] * array.shape[1], array.shape[2])

        self.__axis.pcolormesh(X, y, np.ones_like(cx), color=array, linewidth=0,
                               edgecolors='none',
                               rasterized=True).set_array(None)

    def plot_precomputed_swath_from_cmap(self, array, x, y, swath_number, cmap, norm) -> None:
        y = (120 - y) + 60
        # offset X array by swath number
        X = x + slit_width * swath_number

        self.__axis.pcolormesh(X, y, array, cmap=cmap, norm=norm)


class Colorbar:
    """A class that designates an axis as a colorbar with specified properties.

    This fills an axis with an input colormap. It provides methods to add
    additional information to the colorbar.

    Parameters
    ----------
    axis
        The axis to designate as a colorbar.
    cmap
        The colormap to fill the axis.
    norm
        The normalization to apply to the colormap.

    """
    def __init__(self, axis: plt.Axes, cmap: colors.LinearSegmentedColormap,
                 norm: colors.Normalize) -> None:
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

    @property
    def cmap(self) -> colors.LinearSegmentedColormap:
        return self.__cmap

    @property
    def norm(self) -> colors.Normalize:
        return self.__norm


class QuicklookColorbarBundle(Quicklook, Colorbar):
    """Bundle together QL and its colorbar.

    """
    def __init__(self, quicklook_ax: plt.Axes, colorbar_ax: plt.Axes, cmap,
                 norm) -> None:
        Quicklook.__init__(self, quicklook_ax)
        Colorbar.__init__(self, colorbar_ax, cmap, norm)

    def plot_precomputed_swath_bundle_from_cmap(self, array, x, y, swath_number):
        self.plot_precomputed_swath_from_cmap(array, x, y, swath_number,
                                              self.cmap, self.norm)


class AuxiliaryArray:
    """Abstract base class to read in an auxiliary numpy array.

    This acts like a numpy array, but provides some more convenient error
    handling.

    Parameters
    ----------
    file_path
        Absolute path of the array to read in.

    """
    def __init__(self, file_path: str) -> None:
        self.__file_path = file_path
        self.__array = self.__load_array()

    def __load_array(self) -> np.ndarray:
        try:
            return np.load(self.__file_path)
        except TypeError:
            message = 'file_path must be a string.'
            raise TypeError(message)
        except ValueError:
            message = 'file_path does not point to a numpy array'
            raise ValueError(message)

    def __getattr__(self, method):
        return getattr(self.__array, method)

    @property
    def array(self) -> np.ndarray:
        return self.__array

    @array.setter
    def array(self, val: np.ndarray) -> None:
        self.__array = val


class SurfaceGeographyMap(AuxiliaryArray):
    """Read in an auxiliary geography map.

    This class will read in the standard geographic map used with IUVS data
    unless another file is specified. It otherwise acts like a numpy.ndarray.

    Parameters
    ----------
    file_path
       Absolute path of the array to read in.

    """
    def __init__(self, file_path=None):
        file_path = self.__make_file_path(file_path)
        super().__init__(file_path)

    # TODO: This is fragile and depends on project structure... fix that
    @staticmethod
    def __make_file_path(file) -> str:
        if file is None:
            file = os.path.join(os.getcwd(), '..', '..', 'aux',
                                'mars_surface_map.npy')
        return file


class MagneticFieldMap(AuxiliaryArray):
    """Read in an auxiliary Martian closed magnetic field probability map.

    This class will read in the standard magnetic field map used with IUVS data
    unless another file is specified. It otherwise acts like a numpy.ndarray.

    Parameters
    ----------
    file_path
       Absolute path of the array to read in.

    """
    def __init__(self, file_path=None):

        file_path = self.__make_file_path(file_path)
        super().__init__(file_path)
        self.__make_map_high_resolution()

    # TODO: This is fragile and depends on project structure... fix that
    @staticmethod
    def __make_file_path(file) -> str:
        if file is None:
            file = os.path.join(os.getcwd(), '..', '..', 'aux',
                                'magnetic_field_closed_probability.npy')
        return file

    def __make_map_high_resolution(self):
        self.array = self.__create_high_resolution_map()

    def __create_high_resolution_map(self):
        field = np.flipud(self.array)    # to match the flipped QL I think
        highres_map = self.__resize_map(field)
        return self.__colorize_map(highres_map)

    # TODO: make Zac look into gaussian smoothing with astropy
    @staticmethod
    def __resize_map(map_field):
        map_field = resize(map_field, (1800, 3600))
        V = map_field.copy()
        V[np.isnan(map_field)] = 0
        VV = gaussian_filter(V, sigma=1)
        W = 0 * map_field.copy() + 1
        W[np.isnan(map_field)] = 0
        WW = gaussian_filter(W, sigma=1)
        map_field = VV / WW
        map_field /= np.nanmax(map_field)
        return map_field

    @staticmethod
    def __colorize_map(field):
        colormap = Colormaps()
        colormap.set_magnetic_field()
        return colormap.cmap(colormap.norm(field))


class Colormaps:
    """ A class that holds colormaps.

    Colormaps contains some preset colormaps. Calling any methods changes the
    object's known colormap and norm are.

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
    def cmap(self) -> colors.LinearSegmentedColormap:
        return self.__cmap

    @property
    def norm(self) -> colors.Normalize:
        return self.__norm


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

    def __make_pcolormesh_angles(self):
        angles = self.__file['integration'].data['mirror_deg'] * 2
        dang = np.diff(angles)[0]
        x, y = np.meshgrid(np.linspace(0, slit_width, self.__positions + 1),
                           np.linspace(angles[0] - dang / 2,
                                       angles[-1] + dang / 2, self.__integrations + 1))

        dslit = slit_width / self.__positions

        cx, cy = np.meshgrid(
            np.linspace(0 + dslit, slit_width - dslit, self.__positions),
            np.linspace(angles[0], angles[-1], self.__integrations))

        if self.__flip:
            x = np.fliplr(x)
            y = (np.fliplr(y) - 90) / (-1) + 90
            cx = np.fliplr(cx)
            cy = (np.fliplr(cy) - 90) / (-1) + 90
        return x, y, cx, cy

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
                local_time[i, j] = lt
                solar_zenith_angle[i, j] = sza
                emission_angle[i, j] = ea
                phase_angle[i, j] = pa
                context_map[i, j] = con_map
        x, y, cx, cy = self.__make_pcolormesh_angles()

        self.__arrays.latitude = latitude
        self.__arrays.longitude = longitude
        self.__arrays.local_time = local_time
        self.__arrays.solar_zenith_angle = solar_zenith_angle
        self.__arrays.emission_angle = emission_angle
        self.__arrays.phase_angle = phase_angle
        self.__arrays.context_map = context_map
        self.__arrays.x = x
        self.__arrays.y = y
        self.__arrays.cx = cx
        self.__arrays.cy = cy

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
        self.__x = self.__make_array_of_nans((shape[0] + 1, shape[1] + 1))
        self.__y = self.__make_array_of_nans((shape[0] + 1, shape[1] + 1))
        self.__cx = self.__make_array_of_nans(shape)
        self.__cy = self.__make_array_of_nans(shape)

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

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, val):
        self.__x = val

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, val):
        self.__y = val

    @property
    def cx(self):
        return self.__cx

    @cx.setter
    def cx(self, val):
        self.__cx = val

    @property
    def cy(self):
        return self.__cy

    @cy.setter
    def cy(self, val):
        self.__cy = val


if __name__ == '__main__':
    from pyuvs.files import FileFinder
    files = FileFinder('/media/kyle/Samsung_T5/IUVS_data').soschob(3453, segment='apoapse', channel='muv')
    ff = '/home/kyle/repos/pyuvs/aux/flatfield133.npy'
    sp = '/media/kyle/Samsung_T5/IUVS_data/spice'
    saveloc = '/home/kyle'
    swaths = [0, 0, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5]
    #ql = ApoapseMUVQuicklook(files, np.load(ff), swaths, False, sp)
    #ql.fill_plots_aurora()
    #ql.savefig('/home/kyle/veryVeryGoodJunk.png')
